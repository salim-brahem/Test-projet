from pathlib import Path

def write_reports(context, triage, tasks, applied, failed, tests_ok: bool, correlation_id: str, risks: list[dict], logger) -> dict:
    items = triage.get("items", [])
    counts = {
        "P0": sum(1 for i in items if i.get("priority") == "P0"),
        "P1": sum(1 for i in items if i.get("priority") == "P1"),
        "P2": sum(1 for i in items if i.get("priority") == "P2"),
    }

    qg_status = "UNKNOWN"
    try:
        qg_status = context["quality_gate"]["projectStatus"]["status"]
    except Exception:
        pass

    report = {
        "correlation_id": correlation_id,
        "quality_gate": qg_status,
        "triage_counts": counts,
        "selected_files": triage.get("selected_files", []),
        "tasks": tasks,
        "applied": applied,
        "failed": failed,
        "tests_ok": tests_ok,
        "risks": risks,
    }

    md = []
    md.append("# SonarReview+Refactor Agent Report\n")
    md.append(f"- Correlation ID: `{correlation_id}`")
    md.append(f"- Quality Gate: **{qg_status}**")
    md.append(f"- Triage: P0={counts['P0']} P1={counts['P1']} P2={counts['P2']}")
    md.append(f"- Applied patches: {len(applied)}")
    md.append(f"- Failed patches: {len(failed)}")
    md.append(f"- Tests OK: **{tests_ok}**\n")

    md.append("## Selected files\n")
    for f in triage.get("selected_files", []):
        md.append(f"- `{f}`")

    if applied:
        md.append("\n## Applied\n")
        for a in applied:
            md.append(f"- {a}")

    if failed:
        md.append("\n## Failed\n")
        for f in failed:
            md.append(f"- {f}")

    if risks:
        md.append("\n## Spring/REST/JPA risks (beyond Sonar)\n")
        for r in risks[:30]:
            md.append(f"- **{r.get('priority','P2')}** [{r.get('topic')}] `{r.get('file')}`: {r.get('message')}")
            md.append(f"  - Fix: {r.get('suggested_safe_fix')}")

    Path("artifacts/report.md").write_text("\n".join(md), encoding="utf-8")
    logger.info("Reports written: artifacts/report.md and artifacts/report.json")
    return report
