from __future__ import annotations
import json
from .utils import clamp, extract_snippet, read_text

def build_fix_messages(system_prompt_path: str, user_payload: dict, max_prompt_chars: int) -> list[dict[str,str]]:
    system = read_text(system_prompt_path, "").strip()
    user_json = json.dumps(user_payload, ensure_ascii=False, indent=2)
    user_json = clamp(user_json, max_prompt_chars)
    return [{"role":"system","content":system},{"role":"user","content":user_json}]

def attach_snippets(batch: list[dict], max_lines: int = 25, max_chars: int = 1400) -> list[dict]:
    out = []
    for i in batch:
        file = i.get("file") or ""
        line = i.get("line")
        snip = extract_snippet(file, line, max_lines=max_lines, max_chars=max_chars) if isinstance(file, str) else ""
        ii = dict(i)
        ii["snippet"] = snip
        out.append(ii)
    return out
