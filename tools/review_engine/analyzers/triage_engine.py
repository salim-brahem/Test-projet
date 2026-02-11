import json
from pathlib import Path
from datetime import datetime

from ..config import Config
from ..llm.llm_client import ollama_generate
from ..llm.prompt_router import load_prompt, render
from ..llm.output_parsers import extract_first_json_object


def _write_debug(name: str, content: str) -> str:
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = Path("artifacts") / f"{ts}_{name}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return str(path)


def _chunk(lst, size: int):
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


def _norm_sev(sev: str) -> str:
    return (sev or "").strip().upper()


def _extract_file_from_component(component: str) -> str:
    """
    Sonar 'component' is often like:
      "projectKey:src/main/java/.../File.java"
    We want the file path only.
    """
    c = (component or "").strip()
    if ":" in c:
        return c.split(":", 1)[1]
    return c


def _simplify_issue(issue: dict) -> dict:
    """
    Keep only useful fields to reduce prompt size.
    """
    file_path = _extract_file_from_component(issue.get("component"))
    return {
        "rule": issue.get("rule"),
        "severity": issue.get("severity"),
        "file": file_path,
        "line": issue.get("line"),
        "message": issue.get("message"),
        "type": issue.get("type"),
        # optional: tags can help for security/bug hints; keep if you want
        # "tags": issue.get("tags") or [],
    }


def _merge_triage(base: dict, new: dict) -> dict:
    """
    Merge LLM partial triage outputs into one global triage:
    - dedupe selected_files
    - append items
    """
    base.setdefault("selected_files", [])
    base.setdefault("items", [])

    if isinstance(new, dict):
        for f in (new.get("selected_files") or []):
            if f not in base["selected_files"]:
                base["selected_files"].append(f)

        base["items"].extend(new.get("items") or [])

    return base


def run_triage(cfg: Config, context: dict, logger) -> dict:
    raw_issues = context.get("issues", []) or []
    changed_files = (context.get("git", {}) or {}).get("changed_files", []) or []

    if not raw_issues and not changed_files:
        logger.info("No Sonar issues and no git changes -> skipping LLM.")
        triage = {"selected_files": [], "items": []}
        Path("artifacts/triage.json").write_text(json.dumps(triage, indent=2), encoding="utf-8")
        report = {"reports": {"BLOCKER_CRITICAL": [], "MAJOR": [], "MINOR": []}}
        Path("artifacts/triage_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        return triage

    # Load prompts
    policy = load_prompt("policy.txt")
    tmpl = load_prompt("sonar_triage.txt")

    # Simplify issues to reduce prompt size
    issues = [_simplify_issue(x) for x in raw_issues]

    # Split by severity in the order you want
    blocker_critical = []
    major = []
    minor = []

    for iss in issues:
        sev = _norm_sev(iss.get("severity"))
        if sev in ("BLOCKER", "CRITICAL"):
            blocker_critical.append(iss)
        elif sev == "MAJOR":
            major.append(iss)
        else:
            minor.append(iss)

    groups = [
        ("BLOCKER_CRITICAL", blocker_critical),
        ("MAJOR", major),
        ("MINOR", minor),
    ]

    # This is the pipeline-compatible final triage (same format as your template)
    merged_triage = {"selected_files": [], "items": []}

    # This is the separated report by severity (batch-by-batch outputs)
    report = {"reports": {"BLOCKER_CRITICAL": [], "MAJOR": [], "MINOR": []}}

    for group_name, group_issues in groups:
        if not group_issues:
            continue

        logger.info(f"Triage group {group_name}: {len(group_issues)} issues")

        for batch_idx, batch in enumerate(_chunk(group_issues, 15), start=1):
            # Small context for this batch only
            context_small = {
                "git": {"changed_files": changed_files},
                "issues": batch,
                "meta": {
                    "group": group_name,
                    "batch_index": batch_idx,
                    "batch_size": len(batch),
                    "total_in_group": len(group_issues),
                    # this will help the LLM not assume missing issues exist
                    "note": "Only these issues are included in this batch.",
                },
            }

            prompt = render(
                tmpl,
                {
                    "policy": policy,
                    "max_files": cfg.max_files_to_patch,
                    "context_json": json.dumps(context_small, indent=2),
                },
            )

            prompt_path = _write_debug(f"{group_name.lower()}_batch{batch_idx}_triage_prompt.txt", prompt)
            logger.info(f"LLM PROMPT saved to {prompt_path}")

            out = ollama_generate(cfg.ollama_model, prompt)

            raw_path = _write_debug(f"{group_name.lower()}_batch{batch_idx}_triage_raw.txt", out)
            logger.info(f"LLM RAW OUTPUT saved to {raw_path}")

            try:
                parsed = extract_first_json_object(out)
            except Exception as e:
                logger.error(f"Triage JSON parse failed for {group_name} batch {batch_idx}: {e}")
                parsed = {
                    "selected_files": [],
                    "items": [
                        {
                            "priority": "P2",
                            "file": "-",
                            "rule": "triage_parser",
                            "message": "LLM output was not valid JSON",
                            "why": f"Could not parse JSON for {group_name} batch {batch_idx}",
                            "safe_fix": "Ensure the LLM returns only valid RFC 8259 JSON with the expected schema.",
                        }
                    ],
                }

            # Save batch output in the separated report
            report["reports"][group_name].append(parsed)

            # Merge into a single triage.json for your pipeline
            merged_triage = _merge_triage(merged_triage, parsed)

            # Keep selected_files bounded globally (optional safety)
            if len(merged_triage["selected_files"]) > cfg.max_files_to_patch:
                merged_triage["selected_files"] = merged_triage["selected_files"][: cfg.max_files_to_patch]

    # Write outputs
    Path("artifacts/triage.json").write_text(json.dumps(merged_triage, indent=2), encoding="utf-8")
    Path("artifacts/triage_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    return merged_triage
