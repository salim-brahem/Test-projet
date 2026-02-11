from __future__ import annotations
from typing import Any

def section(title: str, body: str) -> str:
    return f"## {title}\n\n{(body or '').strip()}\n\n"

def build_report(data: dict[str, Any]) -> str:
    parts = ["# AI DevOps Bot — Rapport\n"]
    parts.append(section("Résumé", data.get("summary","")))
    parts.append(section("Fix Sonar Stages", data.get("sonar_md","")))
    parts.append(section("Post-pass Qualité (5 max)", data.get("quality_md","")))
    parts.append(section("Tests", data.get("tests_md","")))
    parts.append(section("Git Push", data.get("push_md","")))
    return "\n".join(parts)
