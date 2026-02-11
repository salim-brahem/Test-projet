import json
import re
from typing import Any, Dict, List


# ---------- JSON extractors ----------

_JSON_OBJ_RE = re.compile(r"\{.*\}", re.DOTALL)
_JSON_ARR_RE = re.compile(r"\[.*\]", re.DOTALL)


def _try_load(s: str) -> Any:
    return json.loads(s)


def extract_first_json_object(text: str) -> Dict[str, Any]:
    """
    Extract the first JSON object {...} from LLM output.
    Accepts:
    - pure JSON
    - JSON inside fenced blocks ```json ... ```
    - JSON mixed with commentary
    """
    if not text:
        raise ValueError("No text provided")

    t = text.strip()

    # Fast path: whole text is JSON object
    if t.startswith("{") and t.endswith("}"):
        obj = _try_load(t)
        if isinstance(obj, dict):
            return obj

    # Try fenced blocks first
    obj = _extract_json_from_fences(t, expect="object")
    if obj is not None:
        return obj

    # Find first {...} (best effort)
    m = _JSON_OBJ_RE.search(t)
    if not m:
        raise ValueError("No JSON object found in text")
    candidate = m.group(0)

    obj = _try_load(candidate)
    if not isinstance(obj, dict):
        raise ValueError("Parsed JSON is not an object")
    return obj


def extract_first_json_array(text: str) -> List[Any]:
    """
    Extract the first JSON array [...] from LLM output.
    Useful when prompt returns a list (e.g. risks).
    """
    if not text:
        raise ValueError("No text provided")

    t = text.strip()

    # Fast path: whole text is JSON array
    if t.startswith("[") and t.endswith("]"):
        arr = _try_load(t)
        if isinstance(arr, list):
            return arr

    # Try fenced blocks first
    arr = _extract_json_from_fences(t, expect="array")
    if arr is not None:
        return arr

    # Find first [...]
    m = _JSON_ARR_RE.search(t)
    if not m:
        raise ValueError("No JSON array found in text")
    candidate = m.group(0)

    arr = _try_load(candidate)
    if not isinstance(arr, list):
        raise ValueError("Parsed JSON is not an array")
    return arr


def _extract_json_from_fences(text: str, expect: str) -> Any | None:
    """
    Extract JSON from fenced code blocks. Returns dict/list or None if not found.
    """
    if "```" not in text:
        return None

    parts = text.split("```")
    # odd indexes are inside fences
    for i in range(1, len(parts), 2):
        block = parts[i].strip()

        # remove optional language label at first line: "json", "javascript", etc.
        lines = block.splitlines()
        if not lines:
            continue

        # If first line is a language token, drop it
        first = lines[0].strip().lower()
        if first in ("json", "javascript", "js", "python", "yaml", "yml", "diff", "patch"):
            block = "\n".join(lines[1:]).strip()

        if not block:
            continue

        # try object/array parse
        try:
            parsed = _try_load(block)
        except Exception:
            continue

        if expect == "object" and isinstance(parsed, dict):
            return parsed
        if expect == "array" and isinstance(parsed, list):
            return parsed

    return None


# ---------- Git diff extractors ----------

# Matches blocks starting with "diff --git" up to next "diff --git" or end
_DIFF_BLOCK_RE = re.compile(r"(^diff --git .*$.*?)(?=^diff --git |\Z)", re.DOTALL | re.MULTILINE)


def looks_like_git_diff(text: str) -> bool:
    """
    Heuristic detector for unified diffs.
    """
    if not text:
        return False
    t = text.strip()
    return (
        "diff --git " in t
        or ("--- " in t and "+++ " in t)
        or ("@@ " in t)
    )


def extract_git_diff(text: str) -> str:
    """
    Extract a git diff from LLM output.
    Supports:
    - raw diff output
    - fenced ```diff ... ``` blocks
    - diff mixed with commentary
    """
    if not text:
        raise ValueError("No text provided")

    t = text.strip()

    # Fast path: starts as a diff
    if t.startswith("diff --git "):
        return t

    # Try fenced blocks
    diff = _extract_diff_from_fences(t)
    if diff is not None:
        return diff

    # Find diff --git blocks
    m = _DIFF_BLOCK_RE.search(t)
    if m:
        return m.group(1).strip()

    # Fallback: unified diff markers without diff --git
    if ("--- " in t and "+++ " in t and "@@" in t):
        idx = t.find("--- ")
        return t[idx:].strip()

    raise ValueError("No git diff found in text")


def _extract_diff_from_fences(text: str) -> str | None:
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
        # Drop language label
        if first in ("diff", "patch"):
            block = "\n".join(lines[1:]).strip()

        if not block:
            continue

        if block.startswith("diff --git ") or ("--- " in block and "+++ " in block and "@@" in block):
            return block.strip()

    return None
