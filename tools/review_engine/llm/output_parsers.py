import json
import re
from typing import Any, Dict, List


# ---------- Helpers ----------

_JSON_OBJ_RE = re.compile(r"\{.*\}", re.DOTALL)
_JSON_ARR_RE = re.compile(r"\[.*\]", re.DOTALL)

_DIFF_BLOCK_RE = re.compile(r"(^diff --git .*$.*?)(?=^diff --git |\Z)", re.DOTALL | re.MULTILINE)


def _strip_json_comments(s: str) -> str:
    # remove //... and /*...*/ (best effort)
    s = re.sub(r"//.*?$", "", s, flags=re.MULTILINE)
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.DOTALL)
    return s


def _remove_trailing_commas(s: str) -> str:
    # ,} or ,]  -> } or ]
    return re.sub(r",\s*([}\]])", r"\1", s)


def _single_to_double_quotes_best_effort(s: str) -> str:
    """
    Best effort conversion:
    - 'key': -> "key":
    - : 'value' -> : "value"
    This is heuristic and intentionally limited.
    """
    s = re.sub(r"(?P<prefix>[\{\s,])'(?P<key>[^'\n\r]+?)'\s*:", r'\g<prefix>"\g<key>":', s)
    s = re.sub(r":\s*'(?P<val>[^'\n\r]*?)'(?P<suffix>[\s,}\]])", r': "\g<val>"\g<suffix>', s)
    return s


def _try_load_json(s: str) -> Any:
    raw = s.strip()
    raw = _strip_json_comments(raw)
    raw = _remove_trailing_commas(raw)

    # 1) strict JSON
    try:
        return json.loads(raw)
    except Exception:
        pass

    # 2) relaxed: single quotes -> double quotes best effort
    relaxed = _single_to_double_quotes_best_effort(raw)
    relaxed = _remove_trailing_commas(relaxed)
    return json.loads(relaxed)


def _extract_from_fences(text: str, wanted: str) -> Any | None:
    """
    Extract JSON from fenced blocks ```json ... ``` or diff from ```diff ... ```
    wanted in {"json_object","json_array","diff"}
    """
    if "```" not in text:
        return None

    parts = text.split("```")
    for i in range(1, len(parts), 2):
        block = parts[i].strip()
        if not block:
            continue

        lines = block.splitlines()
        if not lines:
            continue

        first = lines[0].strip().lower()
        if first in ("json", "javascript", "js", "python", "yaml", "yml", "diff", "patch"):
            block = "\n".join(lines[1:]).strip()

        if not block:
            continue

        if wanted == "diff":
            if block.startswith("diff --git ") or ("--- " in block and "+++ " in block and "@@" in block):
                return block.strip()
            continue

        # wanted json
        try:
            parsed = _try_load_json(block)
        except Exception:
            continue

        if wanted == "json_object" and isinstance(parsed, dict):
            return parsed
        if wanted == "json_array" and isinstance(parsed, list):
            return parsed

    return None


# ---------- Public API: JSON ----------

def extract_first_json_object(text: str) -> Dict[str, Any]:
    if not text:
        raise ValueError("No text provided")

    t = text.strip()

    # whole text
    if t.startswith("{") and t.endswith("}"):
        parsed = _try_load_json(t)
        if isinstance(parsed, dict):
            return parsed

    # fenced blocks
    obj = _extract_from_fences(t, "json_object")
    if obj is not None:
        return obj

    # first {...}
    m = _JSON_OBJ_RE.search(t)
    if not m:
        raise ValueError("No JSON object found in text")

    candidate = m.group(0)
    parsed = _try_load_json(candidate)
    if not isinstance(parsed, dict):
        raise ValueError("Parsed JSON is not an object")
    return parsed


def extract_first_json_array(text: str) -> List[Any]:
    if not text:
        raise ValueError("No text provided")

    t = text.strip()

    # whole text
    if t.startswith("[") and t.endswith("]"):
        parsed = _try_load_json(t)
        if isinstance(parsed, list):
            return parsed

    # fenced blocks
    arr = _extract_from_fences(t, "json_array")
    if arr is not None:
        return arr

    # first [...]
    m = _JSON_ARR_RE.search(t)
    if not m:
        raise ValueError("No JSON array found in text")

    candidate = m.group(0)
    parsed = _try_load_json(candidate)
    if not isinstance(parsed, list):
        raise ValueError("Parsed JSON is not an array")
    return parsed


# ---------- Public API: Git diff ----------

def looks_like_git_diff(text: str) -> bool:
    if not text:
        return False
    t = text.strip()
    return ("diff --git " in t) or ("--- " in t and "+++ " in t) or ("@@ " in t)


def extract_git_diff(text: str) -> str:
    if not text:
        raise ValueError("No text provided")

    t = text.strip()

    if t.startswith("diff --git "):
        return t

    diff = _extract_from_fences(t, "diff")
    if diff is not None:
        return diff

    m = _DIFF_BLOCK_RE.search(t)
    if m:
        return m.group(1).strip()

    if ("--- " in t and "+++ " in t and "@@" in t):
        idx = t.find("--- ")
        return t[idx:].strip()

    raise ValueError("No git diff found in text")
