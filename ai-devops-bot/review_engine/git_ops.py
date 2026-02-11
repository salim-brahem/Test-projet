from __future__ import annotations
from .utils import run_cmd

def changed_files() -> list[str]:
    code, out = run_cmd("git diff --name-only")
    if code != 0:
        return []
    return [x.strip() for x in out.splitlines() if x.strip()]

def checkout_branch(branch: str) -> None:
    run_cmd(f"git checkout -B {branch}")

def commit_all(msg: str) -> None:
    run_cmd("git add -A")
    # commit only if staged changes exist
    code, _ = run_cmd("git diff --cached --quiet")
    if code != 0:
        run_cmd(f"git commit -m \"{msg}\"")

def push(branch: str, remote_url: str | None = None) -> tuple[bool, str]:
    if remote_url and remote_url.strip():
        run_cmd("git remote remove botremote || true")
        run_cmd(f"git remote add botremote \"{remote_url}\"")
        code, out = run_cmd(f"git push botremote {branch}")
        return (code == 0), out[:1500]
    code, out = run_cmd(f"git push origin {branch}")
    return (code == 0), out[:1500]
