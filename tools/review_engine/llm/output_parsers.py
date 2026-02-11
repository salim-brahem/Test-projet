import json
import re
from typing import Any, Dict

_JSON_OBJ_RE = re.compile(r"\{.*\}", re.DOTALL)
_JSON_ARR_RE = re.compile(r"\[.*\]", re.DOTALL)


def _try_load(s: str) -> Any:
    return json.loads(s)


def extract_first_json_object(text: str) -> Dict[str, Any]:
    """
    Extract the first JSON object {...} found in LLM output.
    Raises ValueError if none found or cannot parse.
    """
    if text is None:
        raise ValueError("No text provided")

    # Fast path: whole text is JSON
    t = text.strip()
    if t.startswith("{") and t.endswith("}"):
        obj = _try_load(t)
        if isinstance(obj, dict):
            return obj

    # Search for first {...}
    m = _JSON_OBJ_RE.search(text)
    if not m:
        raise ValueError("No JSON object found in text")

    candidate = m.group(0)
    obj = _try_load(candidate)
    if not isinstance(obj, dict):
        raise ValueError("Parsed JSON is not an object")
    return obj


def extract_first_json_array(text: str) -> list:
    """
    Extract the first JSON array [...] found in LLM output.
    Useful for risks prompt returning a list.
    """
    if text is None:
        raise ValueError("No text provided")

    t = text.strip()
    if t.startswith("[") and t.endswith("]"):
        arr = _try_load(t)
        if isinstance(arr, list):
            return arr

    m = _JSON_ARR_RE.search(text)
    if not m:
        raise ValueError("No JSON array found in text")

    candidate = m.group(0)
    arr = _try_load(candidate)
    if not isinstance(arr, list):
        raise ValueError("Parsed JSON is not an array")
    return arr
