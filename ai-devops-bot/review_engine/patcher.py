from __future__ import annotations

from pathlib import Path
from typing import Any
from .utils import run_cmd


def _detect_app_dir() -> str | None:
    """
    Detect the Maven project directory.
    Priority:
      1) directory that contains ./mvnw
      2) directory that contains pom.xml
    """
    # Common candidates first
    candidates = ["gestion-station-skii", "gestion-station-skii", "gestion-station-ski", "app", "."]

    # Add all first-level dirs too
    for p in Path(".").iterdir():
        if p.is_dir():
            candidates.append(p.name)

    seen = set()
    for name in candidates:
        if name in seen:
            continue
        seen.add(name)
        d = Path(name)
        if not d.is_dir():
            continue
        if (d / "mvnw").is_file():
            return name
        if (d / "pom.xml").is_file():
            return name

    return None


def apply_patch(patch_text: str, artifacts_dir: str) -> tuple[bool, str]:
    if not patch_text or not patch_text.strip():
        return False, "empty patch"

    patch_path = Path(artifacts_dir) / "patch.diff"
    patch_path.write_text(patch_text, encoding="utf-8")

    app_dir = _detect_app_dir()
    if not app_dir:
        return False, "Could not detect app dir (no mvnw/pom.xml found)"

    # Best fix for LLM hunks: --recount
    cmd1 = f'git apply --recount --whitespace=nowarn "{patch_path}"'
    code1, out1 = run_cmd(cmd1, cwd=app_dir)
    if code1 == 0:
        return True, f"git_apply_recount_cwd_{app_dir}"

    cmd2 = f'git apply -3 --recount --whitespace=nowarn "{patch_path}"'
    code2, out2 = run_cmd(cmd2, cwd=app_dir)
    if code2 == 0:
        return True, f"git_apply_3way_recount_cwd_{app_dir}"

    # Last resort
    cmd3 = f'git apply --recount --whitespace=fix "{patch_path}"'
    code3, out3 = run_cmd(cmd3, cwd=app_dir)
    if code3 == 0:
        return True, f"git_apply_recount_fixws_cwd_{app_dir}"

    cmd4 = f'git apply -3 --recount --whitespace=fix "{patch_path}"'
    code4, out4 = run_cmd(cmd4, cwd=app_dir)
    if code4 == 0:
        return True, f"git_apply_3way_recount_fixws_cwd_{app_dir}"

    return False, (out1 + "\n" + out2 + "\n" + out3 + "\n" + out4)[:1500]


def apply_files_fallback(files: Any) -> bool:
    app_dir = _detect_app_dir()
    if not app_dir:
        return False

    if not files:
        return False

    # dict format: {path: content}
    if isinstance(files, dict):
        for path, content in files.items():
            if not isinstance(path, str) or not isinstance(content, str):
                continue
            p = Path(path)
            if not str(p).startswith(app_dir + "/") and not str(p).startswith(app_dir + "\\"):
                p = Path(app_dir) / p
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
                p = Path(path)
                if not str(p).startswith(app_dir + "/") and not str(p).startswith(app_dir + "\\"):
                    p = Path(app_dir) / p
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8")
                wrote = True
        return wrote

    return False
