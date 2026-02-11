from __future__ import annotations

from pathlib import Path
from typing import Any
from .utils import run_cmd


def _try_apply(patch_path: Path, cwd: str | None = None) -> tuple[bool, str, str]:
    """
    Try multiple git apply strategies.
    Returns (ok, method, combined_output)
    """
    # Most important: --recount fixes LLM wrong hunk line counts ("corrupt patch")
    cmds = [
        f'git apply --recount --whitespace=nowarn "{patch_path}"',
        f'git apply -3 --recount --whitespace=nowarn "{patch_path}"',
        # last resort: whitespace=fix (can change files), still with recount
        f'git apply --recount --whitespace=fix "{patch_path}"',
        f'git apply -3 --recount --whitespace=fix "{patch_path}"',
    ]

    outs: list[str] = []
    for idx, cmd in enumerate(cmds, start=1):
        if cwd:
            code, out = run_cmd(cmd, cwd=cwd)
        else:
            code, out = run_cmd(cmd)
        outs.append(out or "")
        if code == 0:
            return True, f"git_apply_variant_{idx}" + (f"_cwd_{cwd}" if cwd else ""), "\n".join(outs)

    return False, "failed", "\n".join(outs)


def apply_patch(patch_text: str, artifacts_dir: str) -> tuple[bool, str]:
    if not patch_text or not patch_text.strip():
        return False, "empty patch"

    patch_path = Path(artifacts_dir) / "patch.diff"
    patch_path.write_text(patch_text, encoding="utf-8")

    # 1) Apply from repo root
    ok, method, out = _try_apply(patch_path, cwd=None)
    if ok:
        return True, method

    # 2) If project is in subdir, retry there (your case)
    app_dir = Path("gestion-station-skii")
    if app_dir.is_dir():
        ok2, method2, out2 = _try_apply(patch_path, cwd=str(app_dir))
        if ok2:
            return True, method2
        return False, (out + "\n" + out2)[:1500]

    return False, out[:1500]


def apply_files_fallback(files: Any) -> bool:
    """
    Accept either:
      - dict: { "path": "content", ... }   (your current format)
      - list: [ { "path": "...", "content": "..." }, ... ]  (common LLM format)
    """
    if not files:
        return False

    # dict format
    if isinstance(files, dict):
        for path, content in files.items():
            if not isinstance(path, str) or not isinstance(content, str):
                continue
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        return True

    # list format
    if isinstance(files, list):
        wrote = False
        for item in files:
            if not isinstance(item, dict):
                continue
            path = item.get("path")
            content = item.get("content")
            if isinstance(path, str) and isinstance(content, str):
                p = Path(path)
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8")
                wrote = True
        return wrote

    return False
