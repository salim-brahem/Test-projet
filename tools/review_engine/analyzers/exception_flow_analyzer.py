from pathlib import Path

def analyze_exception_flow(context: dict) -> list[dict]:
    findings = []
    controllers = context.get("repo_index", {}).get("controllers", [])
    for fp in controllers:
        p = Path(fp)
        if not p.exists():
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")

        if "catch (Exception" in txt:
            findings.append({
                "priority": "P2",
                "topic": "error",
                "file": fp,
                "message": "catch(Exception) détecté → risque swallow exception / 500 masqué.",
                "suggested_safe_fix": "Logger + rethrow ou transformer en ResponseStatusException."
            })

    return _dedupe(findings)

def _dedupe(items: list[dict]) -> list[dict]:
    seen, out = set(), []
    for it in items:
        k = (it.get("topic"), it.get("file"), it.get("message"))
        if k in seen:
            continue
        seen.add(k)
        out.append(it)
    return out
