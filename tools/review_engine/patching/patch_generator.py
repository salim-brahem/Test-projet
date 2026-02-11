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


def _read_file_safely(file_path: str) -> str:
    """
    Lit le contenu du fichier du repo.
    - utf-8 (avec errors replace) pour éviter crash sur encodage.
    """
    if not file_path:
        return ""
    p = Path(file_path)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="replace")


def generate_patch_for_task(cfg: Config, context: dict, task: dict, logger) -> dict:
    """
    task = {
        "file_path": "...",
        "coverage_percent": 78.2,
        "issues": [...],
        ...
    }
    """

    # 1) Charger template + policy
    tmpl = load_prompt("sonar_patch_diff.txt")
    policy_text = load_prompt("policy.txt")

    # 2) Récupérer les variables attendues par le template
    file_path = task.get("file_path")
    coverage_percent = task.get("coverage_percent", -1.0)

    # issues_json: si tu as déjà la liste d'issues dans task, prends-la,
    # sinon fallback depuis context['issues_by_file'][file_path]
    issues = task.get("issues")
    if issues is None:
        issues = (context.get("issues_by_file", {}) or {}).get(file_path, [])
    issues_json = json.dumps(issues, ensure_ascii=False, indent=2)

    # contenu réel du fichier à patcher
    file_content = _read_file_safely(file_path)

    # 3) Render du template
    prompt = render(
        tmpl,
        {
            "policy": policy_text,
            "file_path": file_path,
            "coverage_percent": coverage_percent,
            "issues_json": issues_json,
            "file_content": file_content,
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
        diff = extract_git_diff(out) if looks_like_git_diff(out) else extract_git_diff(out)
    except Exception as e:
        logger.error(f"Patch diff extraction failed: {e}")
        diff = ""

    return {
        "file_path": file_path,
        "patch_output": diff,
        "raw_output": out,
    }
