from __future__ import annotations
from pathlib import Path
from .utils import run_cmd

def apply_patch(patch_text: str, artifacts_dir: str) -> tuple[bool, str]:
    if not patch_text.strip():
        return False, "empty patch"
    patch_path = Path(artifacts_dir) / "patch.diff"
    patch_path.write_text(patch_text, encoding="utf-8")

    code, out = run_cmd(f"git apply --whitespace=fix \"{patch_path}\"")
    if code == 0:
        return True, "git_apply"
    code2, out2 = run_cmd(f"git apply -3 --whitespace=fix \"{patch_path}\"")
    if code2 == 0:
        return True, "git_apply_3way"
    return False, (out + "\n" + out2)[:1500]

def apply_files_fallback(files: dict | None) -> bool:
    if not isinstance(files, dict) or not files:
        return False
    for path, content in files.items():
        if not isinstance(path, str) or not isinstance(content, str):
            continue
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return True
