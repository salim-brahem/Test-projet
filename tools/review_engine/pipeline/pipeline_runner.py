import json
import os
from datetime import datetime
from pathlib import Path

from ..config import Config
from ..exceptions import GuardError
from .guards import run_guards
from .retry import retry
from .budgets import from_config

from ..collectors.context_builder import build_context
from ..analyzers.triage_engine import run_triage
from ..analyzers.risk_engine import run_risk_engine

from ..patching.patch_planner import make_patch_tasks
from ..patching.patch_generator import generate_patch_for_task
from ..patching.patch_validator import validate_patch_output
from ..patching.patch_applier import apply_output_files_mode, apply_output_branch_mode

from ..verification.test_runner import mvn_test
from ..reporting.report_writer import write_reports
from ..reporting.evidence_collector import write_json

def _run_id() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")

def run_pipeline(cfg: Config, logger):
    os.makedirs("artifacts", exist_ok=True)
    run_id = _run_id()
    correlation_id = f"review_{run_id}"
    budgets = from_config(cfg)

    logger.info(f"Starting pipeline run_id={run_id} output_mode={cfg.output_mode}")

    # 1) Guards
    try:
        run_guards(cfg.jacoco_xml_path)
    except GuardError as e:
        logger.info(f"GUARDS_FAILED: {e}")
        raise

    # 2) Context (retry because Sonar API can be flaky)
    context = retry(lambda: build_context(cfg, logger), tries=3, logger=logger)
    Path("artifacts/sonar_context.json").write_text(json.dumps(context, indent=2), encoding="utf-8")
    logger.info("Context collected: artifacts/sonar_context.json")

    # 3) Risk engine (beyond Sonar)
    risks = run_risk_engine(context)
    write_json("artifacts/risks.json", {"findings": risks})
    logger.info(f"Risk findings: {len(risks)}")

    # 4) Triage (LLM)
    triage = retry(lambda: run_triage(cfg, context, logger), tries=2, logger=logger)
    Path("artifacts/triage.json").write_text(json.dumps(triage, indent=2), encoding="utf-8")
    logger.info("Triage written: artifacts/triage.json")

    # 5) Plan patch tasks
    tasks = make_patch_tasks(cfg, context, triage, logger)
    Path("artifacts/patch_tasks.json").write_text(json.dumps(tasks, indent=2), encoding="utf-8")
    logger.info(f"Patch tasks planned: {len(tasks['tasks'])}")

    # Enforce budget: max tasks
    tasks["tasks"] = tasks["tasks"][: budgets.max_tasks]

    # 6) Generate + validate patches
    generated = []
    for it in range(budgets.max_iterations):
        logger.info(f"Patch iteration {it+1}/{budgets.max_iterations}")
        any_generated = False

        for task in tasks["tasks"]:
            if task.get("status") == "DONE":
                continue

            patch_out = retry(lambda: generate_patch_for_task(cfg, context, task, logger), tries=2, logger=logger)
            val = validate_patch_output(cfg, task, patch_out, logger)

            if not val["ok"]:
                task["status"] = "FAILED"
                task["fail_reason"] = val["reason"]
                continue

            task["status"] = "DONE"
            task["patch_output"] = patch_out
            generated.append(task)
            any_generated = True

        if not any_generated:
            break

    # 7) Apply according to OUTPUT_MODE
    if cfg.output_mode == "FILES":
        applied, failed_apply = apply_output_files_mode(cfg, generated, logger)
        tests_ok = True
    else:
        applied, failed_apply = apply_output_branch_mode(cfg, generated, logger)
        tests_ok = mvn_test(logger)

    # 8) Report (includes risks)
    report = write_reports(
        context=context,
        triage=triage,
        tasks=tasks,
        applied=applied,
        failed=failed_apply,
        tests_ok=tests_ok,
        correlation_id=correlation_id,
        risks=risks,
        logger=logger,
    )
    Path("artifacts/report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    logger.info("Done. Reports generated in artifacts/")
    return report
