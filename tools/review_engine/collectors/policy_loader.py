from pathlib import Path
import yaml

def load_policy(path: str = "review-policy.yml") -> dict:
    p = Path(path)
    if not p.exists():
        return {
            "layering": "Controller -> Service -> Repository",
            "dto": "DTO at boundaries; avoid exposing entities",
            "errors": "Use @ControllerAdvice or ResponseStatusException",
            "safe_refactor": True
        }
    return yaml.safe_load(p.read_text(encoding="utf-8", errors="replace")) or {}
