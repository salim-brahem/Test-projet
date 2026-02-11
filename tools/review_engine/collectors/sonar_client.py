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

    def _supports_branch_fallback_get(self, path: str, params: dict) -> dict:
        """
        Essaie avec branch si présent. Si Sonar renvoie une erreur (404/400 souvent),
        réessaye sans branch pour compatibilité Community / anciennes configs.
        """
        try:
            return self.get(path, params=params)
        except SonarError as e:
            msg = str(e)
            # On tente un fallback si la branche semble être la cause
            if "branch" in params and ("404" in msg or "400" in msg):
                params2 = dict(params)
                params2.pop("branch", None)
                return self.get(path, params=params2)
            raise

    # ---- OPTIONAL: Quality Gate (ne doit plus faire planter ton pipeline)
    def quality_gate(self, project_key: str, branch: str | None) -> dict | None:
        params = {"projectKey": project_key}
        if branch:
            params["branch"] = branch

        try:
            return self._supports_branch_fallback_get("/api/qualitygates/project_status", params=params)
        except SonarError as e:
            # Si endpoint absent / non supporté -> on ignore
            if "404" in str(e):
                return None
            raise

    # ---- Metrics / Measures
    def measures(self, project_key: str, branch: str | None, metric_keys: list[str]) -> dict:
        params = {"component": project_key, "metricKeys": ",".join(metric_keys)}
        if branch:
            params["branch"] = branch
        return self._supports_branch_fallback_get("/api/measures/component", params=params)

    # ---- Issues (bugs/vuln/code smells)
    def issues(
        self,
        project_key: str,
        branch: str | None,
        severities=None,
        types=None,
        ps=200,
        statuses=None,
    ) -> dict:
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
        if statuses:
            params["statuses"] = ",".join(statuses)

        return self._supports_branch_fallback_get("/api/issues/search", params=params)

    # ---- Security Hotspots (endpoint à part)
    def hotspots(self, project_key: str, branch: str | None, ps=200) -> dict | None:
        params = {"projectKey": project_key, "ps": ps}
        if branch:
            params["branch"] = branch

        try:
            return self._supports_branch_fallback_get("/api/hotspots/search", params=params)
        except SonarError as e:
            # Si l'API hotspots n'existe pas sur ta version, on ignore
            if "404" in str(e):
                return None
            raise
