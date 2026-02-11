from __future__ import annotations
import requests
from typing import Any

class SonarClient:
    def __init__(self, host_url: str, token: str, timeout: int = 30):
        self.host = host_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.host}{path}"
        auth = (self.token, "") if self.token else None
        r = requests.get(url, params=params, auth=auth, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def issues_all(self, project_key: str, ps: int = 200, max_pages: int = 50) -> dict[str, Any]:
        all_issues: list[dict[str, Any]] = []
        total = 0
        for p in range(1, max_pages + 1):
            data = self._get("/api/issues/search", {
                "componentKeys": project_key,
                "resolved": "false",
                "p": p,
                "ps": ps,
            })
            issues = data.get("issues", []) or []
            paging = data.get("paging") or {}
            total = int(paging.get("total", total))
            all_issues.extend(issues)
            if len(all_issues) >= total:
                break
        return {"issues": all_issues, "total": total}

    def rule_show(self, rule_key: str) -> dict[str, Any]:
        return self._get("/api/rules/show", {"key": rule_key})

def compact_issue(raw: dict[str, Any]) -> dict[str, Any]:
    comp = raw.get("component", "") or ""
    # Sonar returns "projectKey:relative/path"
    if ":" in comp:
        comp = comp.split(":", 1)[1]
    return {
        "source": "sonar",
        "issue_key": raw.get("key"),
        "rule": raw.get("rule"),
        "severity": raw.get("severity"),
        "type": raw.get("type"),
        "file": comp,
        "line": raw.get("line"),
        "message": (raw.get("message") or "")[:280],
    }
