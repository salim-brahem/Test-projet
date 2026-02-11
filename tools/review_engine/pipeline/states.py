from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass
class ContextState:
    context: Dict[str, Any]
    path: str = "artifacts/sonar_context.json"

@dataclass
class TriageState:
    triage: Dict[str, Any]
    path: str = "artifacts/triage.json"

@dataclass
class PatchTasksState:
    tasks: Dict[str, Any]
    path: str = "artifacts/patch_tasks.json"

@dataclass
class ApplyState:
    applied: List[Dict[str, Any]] = field(default_factory=list)
    failed: List[Dict[str, Any]] = field(default_factory=list)
    tests_ok: bool = True

@dataclass
class RiskState:
    findings: List[Dict[str, Any]] = field(default_factory=list)
    path: str = "artifacts/risks.json"
