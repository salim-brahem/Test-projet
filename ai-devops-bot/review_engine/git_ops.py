from __future__ import annotations

from pathlib import Path
from .utils import run_cmd


def _detect_app_dir() -> str | None:
    candidates = ["gestion-station-skii", "gestion-station-skii", "gestion-station-ski", "app", "."]
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
        if (d / "mvnw").is_file() or (d / "pom.xml").is_file():
            return name
    return None


def _git(cmd: str) -> tuple[int, str]:
    app_dir = _detect_app_dir()
    if not app_dir:
        return 1, "Could not detect app dir (no mvnw/pom.xml found)"
    return run_cmd(cmd, cwd=app_dir)


def changed_files() -> list[str]:
    app_dir = _detect_app_dir()
    if not app_dir:
        return []
    code, out = run_cmd("git diff --name-only", cwd=app_dir)
    if code != 0:
        return []
    return [f"{app_dir}/" + x.strip() for x in out.splitlines() if x.strip()]


def checkout_branch(branch: str) -> None:
    _git(f"git checkout -B {branch}")


def commit_all(msg: str) -> None:
    _git("git add -A")
    code, _ = _git("git diff --cached --quiet")
    if code != 0:
        _git(f'git commit -m "{msg}"')


def push(branch: str, remote_url: str | None = None) -> tuple[bool, str]:
    if remote_url and remote_url.strip():
        _git("git remote remove botremote || true")
        _git(f'git remote add botremote "{remote_url}"')
        code, out = _git(f"git push botremote {branch}")
        return (code == 0), out[:1500]
    code, out = _git(f"git push origin {branch}")
    return (code == 0), out[:1500]
