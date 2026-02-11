import json
from pathlib import Path
from ..config import Config
from ..llm.llm_client import ollama_generate
from ..llm.prompt_router import load_prompt, render
from ..llm.output_parsers import extract_git_diff, looks_like_git_diff

def _read_file(fp: str) -> str:
    p = Path(fp)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="replace")

def generate_patch_for_task(cfg: Config, context: dict, task: dict, logger) -> str:
    policy = load_prompt("policy.txt")

    file_path = task["file_path"]
    content = _read_file(file_path)
    issues = task.get("issues", [])
    cov = task.get("coverage_percent", -1)

    if cfg.output_mode == "FILES":
        tmpl = load_prompt("sonar_patch_files.txt")
        prompt = render(tmpl, {
            "policy": policy,
            "file_path": file_path,
            "coverage_percent": cov,
            "issues_json": json.dumps(issues, indent=2),
            "file_content": content[:25000],
        })
        out = ollama_generate(cfg.ollama_model, prompt)
        return out

    tmpl = load_prompt("sonar_patch_diff.txt")
    prompt = render(tmpl, {
        "policy": policy,
        "file_path": file_path,
        "coverage_percent": cov,
        "issues_json": json.dumps(issues, indent=2),
        "file_content": content[:25000],
    })

    out = ollama_generate(cfg.ollama_model, prompt)
    diff = extract_git_diff(out)
    # If model didn't output proper diff, keep raw for validator to fail
    return diff if looks_like_git_diff(diff) else out
