from __future__ import annotations

from pathlib import Path
from typing import Any
from .utils import run_cmd


APP_DIR = "gestion-station-skii"


def apply_patch(patch_text: str, artifacts_dir: str) -> tuple[bool, str]:
    if not patch_text or not patch_text.strip():
        return False, "empty patch"

    patch_path = Path(artifacts_dir) / "patch.diff"
    patch_path.write_text(patch_text, encoding="utf-8")

    # Always apply inside the actual Maven project folder
    if not Path(APP_DIR).is_dir():
        return False, f"APP_DIR not found: {APP_DIR}"

    # Best fix for LLM hunks: --recount
    cmd1 = f'git apply --recount --whitespace=nowarn "{patch_path}"'
    code1, out1 = run_cmd(cmd1, cwd=APP_DIR)
    if code1 == 0:
        return True, "git_apply_recount_appdir"

    cmd2 = f'git apply -3 --recount --whitespace=nowarn "{patch_path}"'
    code2, out2 = run_cmd(cmd2, cwd=APP_DIR)
    if code2 == 0:
        return True, "git_apply_3way_recount_appdir"

    # Last resort
    cmd3 = f'git apply --recount --whitespace=fix "{patch_path}"'
    code3, out3 = run_cmd(cmd3, cwd=APP_DIR)
    if code3 == 0:
        return True, "git_apply_recount_fixws_appdir"

    cmd4 = f'git apply -3 --recount --whitespace=fix "{patch_path}"'
    code4, out4 = run_cmd(cmd4, cwd=APP_DIR)
    if code4 == 0:
        return True, "git_apply_3way_recount_fixws_appdir"

    return False, (out1 + "\n" + out2 + "\n" + out3 + "\n" + out4)[:1500]


def apply_files_fallback(files: Any) -> bool:
    if not files:
        return False

    # dict format: {path: content}
    if isinstance(files, dict):
        for path, content in files.items():
            if not isinstance(path, str) or not isinstance(content, str):
                continue
            p = Path(APP_DIR) / path if not path.startswith(APP_DIR + "/") else Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        return True

    # list format: [{"path": "...", "content": "..."}]
    if isinstance(files, list):
        wrote = False
        for item in files:
            if not isinstance(item, dict):
                continue
            path = item.get("path")
            content = item.get("content")
            if isinstance(path, str) and isinstance(content, str):
                p = Path(APP_DIR) / path if not path.startswith(APP_DIR + "/") else Path(path)
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8")
                wrote = True
        return wrote

    return False
