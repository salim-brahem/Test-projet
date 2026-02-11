from pathlib import Path

PROMPT_DIR = Path("tools/review_engine/llm/prompt_templates")

def load_prompt(name: str) -> str:
    p = PROMPT_DIR / name
    return p.read_text(encoding="utf-8", errors="replace")

def render(template: str, variables: dict) -> str:
    out = template
    for k, v in variables.items():
        out = out.replace("{{" + k + "}}", str(v))
    return out
