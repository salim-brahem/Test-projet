from __future__ import annotations

import json
import re
from typing import Any


def _strip_fences(text: str) -> str:
    """
    Remove ```json ... ``` / ``` ... ``` fences safely.
    """
    if not text:
        return ""
    t = text.strip()

    # remove starting fence like ```json or ```
    t = re.sub(r"^\s*```[a-zA-Z0-9_-]*\s*", "", t)

    # remove trailing fence ```
    t = re.sub(r"\s*```\s*$", "", t)

    return t.strip()


def _extract_first_balanced_object(text: str) -> str | None:
    """
    Return the first balanced {...} JSON object substring.
    Uses brace balancing (doesn't rely on regex).
    """
    if not text:
        return None

    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]

    return None


def parse_fix_response(llm_text: str) -> dict[str, Any]:
    raw = llm_text or ""
    cleaned = _strip_fences(raw)

    # Try: extract first balanced JSON object and parse it
    obj_str = _extract_first_balanced_object(cleaned)
    if obj_str:
        try:
            obj = json.loads(obj_str)
            if isinstance(obj, dict):
                return {
                    "ok": True,
                    "patch": obj.get("patch", "") or "",
                    "summary": obj.get("summary", "") or "",
                    "rationale": obj.get("rationale", "") or "",
                    "policy_compliance": obj.get("policy_compliance", []),
                    "files": obj.get("files"),
                    "raw_obj": obj,
                }
        except json.JSONDecodeError:
            pass

    # Fallback: maybe cleaned is pure JSON
    try:
        obj = json.loads(cleaned)
        if isinstance(obj, dict):
            return {
                "ok": True,
                "patch": obj.get("patch", "") or "",
                "summary": obj.get("summary", "") or "",
                "rationale": obj.get("rationale", "") or "",
                "policy_compliance": obj.get("policy_compliance", []),
                "files": obj.get("files"),
                "raw_obj": obj,
            }
    except json.JSONDecodeError:
        pass

    return {"ok": False, "error": "No JSON found", "patch": "", "files": None, "raw": raw}
