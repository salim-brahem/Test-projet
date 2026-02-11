import base64
import requests
from ..exceptions import SonarError

class SonarClient:
    def __init__(self, host_url: str, token: str, timeout=30):
        self.host_url = host_url.rstrip("/")
        auth = base64.b64encode(f"{token}:".encode()).decode()
        self.headers = {"Authorization": f"Basic {auth}"}
        self.timeout = timeout

    def get(self, path: str, params=None) -> dict:
        url = f"{self.host_url}{path}"
        try:
            r = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            raise SonarError(f"Sonar API failed: {path} err={e}") from e

    def quality_gate(self, project_key: str, branch: str | None) -> dict:
        params = {"projectKey": project_key}
        if branch:
            params["branch"] = branch
        return self.get("/api/qualitygates/project_status", params=params)

    def measures(self, project_key: str, branch: str | None, metric_keys: list[str]) -> dict:
        params = {"component": project_key, "metricKeys": ",".join(metric_keys)}
        if branch:
            params["branch"] = branch
        return self.get("/api/measures/component", params=params)

    def issues(self, project_key: str, branch: str | None, severities=None, types=None, ps=200) -> dict:
        params = {
            "componentKeys": project_key,
            "resolved": "false",
            "ps": ps,
            "s": "SEVERITY",
        }
        if branch:
            params["branch"] = branch
        if severities:
            params["severities"] = ",".join(severities)
        if types:
            params["types"] = ",".join(types)
        return self.get("/api/issues/search", params=params)
