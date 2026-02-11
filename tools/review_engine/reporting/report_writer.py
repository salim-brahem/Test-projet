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
    tasks,
    applied,
    failed,
    tests_ok: bool,
    correlation_id: str,
    risks: list[dict],
    logger,
) -> dict:
    qg_status = _safe_qg_status(context or {})

    selected_files = []
    if isinstance(tasks, dict):
        selected_files = tasks.get("selected_files", []) or []

    report = {
        "correlation_id": correlation_id,
        "quality_gate": qg_status,
        "selected_files": selected_files,
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
    md.append(f"- Selected files: {len(selected_files)}")
    md.append(f"- Applied patches: {len(report['applied'])}")
    md.append(f"- Failed patches: {len(report['failed'])}")
    md.append(f"- Tests OK: **{report['tests_ok']}**\n")

    md.append("## Selected files\n")
    for f in selected_files:
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
            md.app
