import json
from pathlib import Path
from datetime import datetime

from ..config import Config
from ..llm.llm_client import ollama_generate
from ..llm.prompt_router import load_prompt, render
from ..llm.output_parsers import extract_first_json_object


def _write_debug(name: str, content: str):
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = Path("artifacts") / f"{ts}_{name}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return str(path)


def _chunk(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


def _norm_sev(sev: str) -> str:
    return (sev or "").strip().upper()


def run_triage(cfg: Config, context: dict, logger) -> dict:
    issues = context.get("issues", []) or []
    changed_files = (context.get("git", {}) or {}).get("changed_files", []) or []

    if not issues and not changed_files:
        logger.info("No Sonar issues and no git changes -> skipping LLM.")
        result = {"reports": {"BLOCKER_CRITICAL": [], "MAJOR": [], "MINOR": []}}
        Path("artifacts/triage_report.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result

    policy = load_prompt("policy.txt")
    tmpl = load_prompt("sonar_triage.txt")  # tu peux aussi créer un prompt dédié "sonar_report.txt"

    # 1) Split par sévérité
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
            # MINOR + INFO + UNKNOWN -> groupe faible
            minor.append(iss)

    groups = [
        ("BLOCKER_CRITICAL", blocker_critical),
        ("MAJOR", major),
        ("MINOR", minor),
    ]

    final = {"reports": {"BLOCKER_CRITICAL": [], "MAJOR": [], "MINOR": []}}

    # 2) Batch de 15 max, et appel LLM pour chaque batch
    for group_name, group_issues in groups:
        if not group_issues:
            continue

        for batch_idx, batch in enumerate(_chunk(group_issues, 15), start=1):
            context_small = {
                "git": {"changed_files": changed_files},
                "issues": batch,
                "meta": {
                    "group": group_name,
                    "batch_index": batch_idx,
                    "batch_size": len(batch),
                    "total_in_group": len(group_issues),
                    "instruction": (
                        "Produce a concise report for ONLY these issues. "
                        "Focus on actionable fixes, group by file, and call out security/bug impact."
                    ),
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
                logger.error(f"Report JSON parse failed for {group_name} batch {batch_idx}: {e}")
                parsed = {
                    "error": "json_parse_failed",
                    "group": group_name,
                    "batch_index": batch_idx,
                    "raw_preview": out[:800],
                }

            final["reports"][group_name].append(parsed)

    Path("artifacts/triage_report.json").write_text(json.dumps(final, indent=2), encoding="utf-8")
    return final
