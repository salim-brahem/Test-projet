from pathlib import Path

def check_rest_contract(context: dict) -> list[dict]:
    findings = []
    controllers = context.get("repo_index", {}).get("controllers", [])

    for fp in controllers:
        p = Path(fp)
        if not p.exists():
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")

        # Missing explicit status in create endpoints (heuristic)
        if "@PostMapping" in txt and "ResponseEntity" not in txt:
            findings.append({
                "priority": "P2",
                "topic": "rest",
                "file": fp,
                "message": "@PostMapping sans ResponseEntity → statut 201/Location potentiellement non géré.",
                "suggested_safe_fix": "Utiliser ResponseEntity (sans changer route) pour clarifier status codes."
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
