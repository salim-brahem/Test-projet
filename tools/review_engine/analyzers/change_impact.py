def estimate_impact(context: dict, file_path: str, coverage: float | None) -> dict:
    idx = context.get("repo_index", {})
    layer = "other"
    if file_path in idx.get("controllers", []):
        layer = "controller"
    elif file_path in idx.get("services", []):
        layer = "service"
    elif file_path in idx.get("repositories", []):
        layer = "repository"
    elif file_path in idx.get("entities", []):
        layer = "entity"

    base = {"controller": 70, "service": 60, "repository": 55, "entity": 65}.get(layer, 40)
    cov_bonus = 0
    if coverage is not None and coverage >= 0:
        cov_bonus = min(20, int(coverage / 5))
    score = min(100, base + cov_bonus)

    risk = "LOW"
    if score >= 80:
        risk = "HIGH"
    elif score >= 60:
        risk = "MED"

    return {"layer": layer, "impact_score": score, "risk_level": risk}
