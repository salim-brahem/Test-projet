from __future__ import annotations
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
import re
import yaml

@dataclass
class Issue:
    source: str
    severity: str
    type: str
    rule: str
    file: str
    line: int
    message: str
    hint: str | None = None

def load_internal_rules(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8", errors="replace")) or {}

def scan_internal(repo_root: str, rules_path: str) -> list[Issue]:
    data = load_internal_rules(rules_path)
    rules = data.get("rules", []) or []
    root = Path(repo_root)

    ignore_dirs = {"target",".git",".idea",".vscode","node_modules","build","dist"}
    issues: list[Issue] = []

    for f in root.rglob("*"):
        if f.is_dir():
            continue
        if any(part in ignore_dirs for part in f.parts):
            continue
        rel = str(f.relative_to(root)).replace("\\", "/")
        txt = f.read_text(encoding="utf-8", errors="replace")
        lines = txt.splitlines()

        for r in rules:
            globs = r.get("file_globs", []) or []
            if globs and not any(fnmatch(rel, g) for g in globs):
                continue
            rx = re.compile(r.get("regex"))
            for idx, line in enumerate(lines, start=1):
                if rx.search(line):
                    issues.append(Issue(
                        source="internal",
                        severity=r.get("severity","MAJOR"),
                        type="POLICY",
                        rule=r.get("id","INTERNAL_RULE"),
                        file=rel,
                        line=idx,
                        message=r.get("message",""),
                        hint=r.get("fix_hint"),
                    ))
                    break
    return issues
