import json
from pathlib import Path
from datetime import datetime

from ..config import Config
from ..llm.llm_client import ollama_generate
from ..llm.prompt_router import load_prompt, render
from ..llm.output_parsers import extract_git_diff, looks_like_git_diff


def _write_debug(name: str, content: str):
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = Path("artifacts") / f"{ts}_{name}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return str(path)


def generate_patch_for_task(cfg: Config, task: dict, context: dict, logger) -> dict:
    """
    task = {
        "file_path": "...",
        "priority": "...",
        "rule": "...",
        "message": "...",
        ...
    }
    """

    tmpl = load_prompt("sonar_patch_diff.txt")

    prompt = render(
        tmpl,
        {
            "file_path": task.get("file_path"),
            "task_json": json.dumps(task, indent=2),
            "context_json": json.dumps(context, indent=2),
        },
    )

    # 🔥 SAVE PATCH PROMPT
    prompt_path = _write_debug("patch_prompt.txt", prompt)
    logger.info(f"PATCH PROMPT saved to {prompt_path}")

    print("\n========== PATCH LLM INPUT ==========\n")
    print(prompt[:4000])
    print("\n=====================================\n")

    # 🔥 CALL LLM
    out = ollama_generate(cfg.ollama_model, prompt)

    # 🔥 SAVE RAW OUTPUT
    raw_path = _write_debug("patch_raw.txt", out)
    logger.info(f"PATCH RAW OUTPUT saved to {raw_path}")

    print("\n========== PATCH LLM RAW OUTPUT ==========\n")
    print(out[:4000])
    print("\n==========================================\n")

    # 🔥 Try extract diff safely
    try:
        if looks_like_git_diff(out):
            diff = extract_git_diff(out)
        else:
            diff = extract_git_diff(out)
    except Exception as e:
        logger.error(f"Patch diff extraction failed: {e}")
        diff = ""

    return {
        "file_path": task.get("file_path"),
        "patch_output": diff,
        "raw_output": out,
    }
