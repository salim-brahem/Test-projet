from __future__ import annotations
from dataclasses import dataclass
import re
from pathlib import Path

@dataclass
class StrictIssue:
    source: str
    severity: str
    type: str
    rule: str
    file: str
    line: int
    message: str
    hint: str | None = None

def strict_checks(repo_root: str, changed_files: list[str], patch_text: str) -> list[StrictIssue]:
    issues: list[StrictIssue] = []

    # 1) tests required for logic changes
    norm = [c.replace("\\","/") for c in changed_files]
    logic_changed = any(c.startswith("src/main/java/") and ("/service/" in c or "/domain/" in c) for c in norm)
    tests_changed = any(c.startswith("src/test/java/") for c in norm)
    if logic_changed and not tests_changed:
        issues.append(StrictIssue(
            source="strict", severity="CRITICAL", type="POLICY",
            rule="TESTS_REQUIRED_FOR_LOGIC_CHANGES",
            file="(project)", line=0,
            message="Service/domain logic changed but no tests updated.",
            hint="Add/update tests under src/test/java for modified services."
        ))

    # 2) no sensitive data in logs (scan added lines)
    sensitive = re.compile(r"(?i)(password|passwd|pwd|token|secret|authorization|bearer|ssn|email)")
    logcall = re.compile(r"(?i)\b(log\.|logger\.)\w+\(")
    for ln in patch_text.splitlines():
        if ln.startswith("+") and not ln.startswith("+++"):
            if logcall.search(ln) and sensitive.search(ln):
                issues.append(StrictIssue(
                    source="strict", severity="CRITICAL", type="POLICY",
                    rule="NO_SENSITIVE_DATA_IN_LOGS",
                    file="(diff)", line=0,
                    message="Potential sensitive data in logs (added line).",
                    hint="Remove/mask sensitive values; avoid logging headers/tokens/passwords."
                ))
                break

    # 3) layered architecture (simple): controller should not inject repository
    root = Path(repo_root)
    for c in norm:
        if not c.endswith(".java"):
            continue
        p = root / c
        if not p.exists():
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")
        if "@RestController" in txt or c.endswith("Controller.java"):
            if re.search(r"\b[A-Za-z0-9_]*Repository\b", txt) and re.search(r"private\s+final\s+.*Repository", txt):
                issues.append(StrictIssue(
                    source="strict", severity="MAJOR", type="POLICY",
                    rule="LAYERED_ARCHITECTURE",
                    file=c, line=0,
                    message="Controller injects Repository directly.",
                    hint="Inject a Service instead; move repository calls into service layer."
                ))
                break

    return issues
