from __future__ import annotations

import json
from pathlib import Path


def _safe_qg_status(context: dict) -> str:
    """
    - Si quality gate absent (None) => SKIPPED
    - Si présent => status Sonar (OK/ERROR/WARN...) si disponible
    - Sinon => UNKNOWN
    """
    qg = context.get("quality_gate")
    if not qg:
        return "SKIPPED"

    try:
        status = qg.get("projectStatus", {}).get("status")
        return status or "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def write_reports(
    context,
    triage,
    tasks,
    applied,
    failed,
    tests_ok: bool,
    correlation_id: str,
    risks: list[dict],
    logger,
) -> dict:
    triage = triage or {}
    items = triage.get("items", []) or []

    counts = {
        "P0": sum(1 for i in items if i.get("priority") == "P0"),
        "P1": sum(1 for i in items if i.get("priority") == "P1"),
        "P2": sum(1 for i in items if i.get("priority") == "P2"),
    }

    qg_status = _safe_qg_status(context or {})





    report = {
        "correlation_id": correlation_id,
        "quality_gate": qg_status,
        "triage_counts": counts,
        "selected_files": triage.get("selected_files", []) or [],
        "tasks": tasks or [],
        "applied": applied or [],
        "failed": failed or [],
        "tests_ok": bool(tests_ok),
        "risks": risks or [],
    }

    # --- Markdown report
    md = []
    md.append("# SonarReview+Refactor Agent Report\n")
    md.append(f"- Correlation ID: `{correlation_id}`")
    md.append(f"- Quality Gate: **{qg_status}**")
    md.append(f"- Triage: P0={counts['P0']} P1={counts['P1']} P2={counts['P2']}")
    md.append(f"- Applied patches: {len(report['applied'])}")
    md.append(f"- Failed patches: {len(report['failed'])}")
    md.append(f"- Tests OK: **{report['tests_ok']}**\n")

    md.append("## Selected files\n")
    for f in report["selected_files"]:
        md.append(f"- `{f}`")

    if report["applied"]:
        md.append("\n## Applied\n")
        for a in report["applied"]:
            md.append(f"- {a}")

    if report["failed"]:
        md.append("\n## Failed\n")
        for f in report["failed"]:
            md.append(f"- {f}")

    if report["risks"]:
        md.append("\n## Spring/REST/JPA risks (beyond Sonar)\n")
        for r in report["risks"][:30]:
            prio = r.get("priority", "P2")
            topic = r.get("topic", "risk")
            file_ = r.get("file", "?")
            msg = r.get("message", "")
            fix = r.get("suggested_safe_fix", "")
            md.append(f"- **{prio}** [{topic}] `{file_}`: {msg}")
            if fix:
                md.append(f"  - Fix: {fix}")

    # --- Write artifacts
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    (artifacts_dir / "report.md").write_text("\n".join(md), encoding="utf-8")
    (artifacts_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


    logger.info("Reports written: artifacts/report.md and artifacts/report.json")
    return report