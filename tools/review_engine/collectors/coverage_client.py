import subprocess
from typing import List

def _run(cmd: List[str]) -> str:
    out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    return out.decode("utf-8", errors="replace")

def changed_files(base_ref: str) -> List[str]:
    txt = _run(["git", "diff", "--name-only", f"{base_ref}...HEAD"])
    return [l.strip() for l in txt.splitlines() if l.strip()]

def diff_text(base_ref: str) -> str:
    return _run(["git", "diff", f"{base_ref}...HEAD"])

def create_branch(name: str):
    _run(["git", "checkout", "-b", name])

def checkout(name: str):
    _run(["git", "checkout", name])

def add_all():
    _run(["git", "add", "."])

def commit(msg: str):
    _run(["git", "commit", "-m", msg])

def push(branch: str):
    _run(["git", "push", "origin", branch])
