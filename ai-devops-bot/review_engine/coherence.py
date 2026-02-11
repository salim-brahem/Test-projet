from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re

@dataclass
class CoherenceIssue:
    source: str
    severity: str
    type: str
    rule: str
    file: str
    line: int
    message: str
    hint: str | None = None

def detect_coherence(repo_root: str, changed_files: list[str]) -> list[CoherenceIssue]:
    """
    Simple heuristics (pas d'AST, pas complexe) pour détecter :
    - DTO consistency (si DTO modifié, vérifier qu'il existe un mapper/service/controller associé)
    - Error handling (Optional.get(), catch vide) sur fichiers modifiés
    """
    root = Path(repo_root)
    norm = [c.replace("\\","/") for c in changed_files]
    issues: list[CoherenceIssue] = []

    # DTO consistency: si un *Dto*.java modifié -> demander de vérifier mapper/controller/client/tests
    dto_files = [c for c in norm if c.endswith(".java") and re.search(r"(?i)\bDto\b", Path(c).name)]
    for dto in dto_files:
        issues.append(CoherenceIssue(
            source="coherence", severity="MAJOR", type="COHERENCE",
            rule="DTO_CONSISTENCY",
            file=dto, line=0,
            message="DTO changed; ensure mappers/controllers/clients/tests are updated accordingly.",
            hint="Check MapStruct/manual mappers + controllers + any clients + tests compilation."
        ))

    # Error handling checks on changed java files
    for c in norm:
        if not c.endswith(".java"):
            continue
        p = root / c
        if not p.exists():
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")
        if "Optional" in txt and re.search(r"\.get\(\)\s*;", txt):
            issues.append(CoherenceIssue(
                source="coherence", severity="MAJOR", type="COHERENCE",
                rule="ERROR_HANDLING",
                file=c, line=0,
                message="Possible Optional.get() without check.",
                hint="Use orElseThrow / isPresent / orElse."
            ))
        if re.search(r"catch\s*\([^)]*\)\s*\{\s*\}", txt):
            issues.append(CoherenceIssue(
                source="coherence", severity="MAJOR", type="COHERENCE",
                rule="ERROR_HANDLING",
                file=c, line=0,
                message="Empty catch block found.",
                hint="Log and/or rethrow; never silently swallow exceptions."
            ))

    return issues
