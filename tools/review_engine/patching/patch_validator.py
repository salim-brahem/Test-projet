import json
from ..config import Config
from ..llm.output_parsers import looks_like_git_diff, extract_first_json_object
from .patch_safety import (
    touches_pom,
    diff_touches_rest_mapping,
    diff_changes_public_signature,
    diff_too_large
)

def validate_patch_output(cfg: Config, task: dict, patch_out: str, logger) -> dict:
    fp = task["file_path"]

    if touches_pom(fp):
        return {"ok": False, "reason": "Refusing to patch pom.xml"}

    if cfg.output_mode == "FILES":
        # Must be strict JSON with files[]
        try:
            obj = extract_first_json_object(patch_out)
        except Exception:
            return {"ok": False, "reason": "FILES mode requires JSON output with files[]"}
        if "files" not in obj or not isinstance(obj["files"], list) or len(obj["files"]) == 0:
            return {"ok": False, "reason": "FILES JSON missing files[]"}
        return {"ok": True, "reason": "ok"}

    # DIFF mode
    if not looks_like_git_diff(patch_out):
        return {"ok": False, "reason": "Not a valid git unified diff"}

    if diff_too_large(patch_out, int(task.get("max_change_lines", 120))):
        return {"ok": False, "reason": "Diff too large for safe refactor budget"}

    if diff_changes_public_signature(patch_out):
        return {"ok": False, "reason": "Patch seems to change public/protected signatures (blocked)"}

    if diff_touches_rest_mapping(patch_out):
        return {"ok": False, "reason": "Patch touches REST mapping annotations (blocked)"}

    return {"ok": True, "reason": "ok"}
