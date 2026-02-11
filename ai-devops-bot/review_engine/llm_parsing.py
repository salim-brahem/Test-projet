from __future__ import annotations
import json
from typing import Any

def extract_first_json(text: str) -> dict[str, Any] | None:
    if not text:
        return None
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                candidate = text[start:i+1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    continue
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return None

def parse_fix_response(llm_text: str) -> dict[str, Any]:
    obj = extract_first_json(llm_text)
    if obj is None:
        return {"ok": False, "error": "No JSON found", "patch": "", "files": None, "raw": llm_text}
    return {
        "ok": True,
        "patch": obj.get("patch","") or "",
        "summary": obj.get("summary","") or "",
        "rationale": obj.get("rationale","") or "",
        "policy_compliance": obj.get("policy_compliance", []),
        "files": obj.get("files"),
        "raw_obj": obj,
    }
