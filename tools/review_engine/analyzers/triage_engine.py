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


def run_triage(cfg: Config, context: dict, logger) -> dict:
    issues = context.get("issues", []) or []
    changed = (context.get("git", {}) or {}).get("changed_files", []) or []

    if len(issues) == 0 and len(changed) == 0:
        logger.info("No Sonar issues and no git changes -> skipping LLM.")
        triage = {"selected_files": [], "items": []}
        Path("artifacts/triage.json").write_text(json.dumps(triage, indent=2))
        return triage

    policy = load_prompt("policy.txt")
    tmpl = load_prompt("sonar_triage.txt")

    prompt = render(
        tmpl,
        {
            "policy": policy,
            "max_files": cfg.max_files_to_patch,
            "context_json": json.dumps(context, indent=2),
        },
    )

    # 🔥 SAVE PROMPT
    prompt_path = _write_debug("triage_prompt.txt", prompt)
    logger.info(f"LLM PROMPT saved to {prompt_path}")

    print("\n========== LLM INPUT (PROMPT) ==========\n")
    print(prompt[:4000])  # limit console size
    print("\n========================================\n")

    # 🔥 CALL LLM
    out = ollama_generate(cfg.ollama_model, prompt)

    # 🔥 SAVE RAW OUTPUT
    raw_path = _write_debug("triage_raw.txt", out)
    logger.info(f"LLM RAW OUTPUT saved to {raw_path}")

    print("\n========== LLM RAW OUTPUT ==========\n")
    print(out[:4000])  # limit console size
    print("\n====================================\n")

    try:
        triage = extract_first_json_object(out)
    except Exception as e:
        logger.error(f"Triage JSON parse failed: {e}")
        triage = {"selected_files": [], "items": []}

    Path("artifacts/triage.json").write_text(json.dumps(triage, indent=2))

    return triage
