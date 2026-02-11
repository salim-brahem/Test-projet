from pathlib import Path

def analyze_jpa(context: dict) -> list[dict]:
    findings = []
    entities = context.get("repo_index", {}).get("entities", [])
    for fp in entities:
        p = Path(fp)
        if not p.exists():
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")

        if "FetchType.EAGER" in txt:
            findings.append({
                "priority": "P2",
                "topic": "jpa",
                "file": fp,
                "message": "FetchType.EAGER détecté (risque perf / N+1).",
                "suggested_safe_fix": "Préférer LAZY et fetch join ciblé au repository si nécessaire."
            })

        if "@OneToMany" in txt and "mappedBy" not in txt:
            findings.append({
                "priority": "P2",
                "topic": "jpa",
                "file": fp,
                "message": "@OneToMany sans mappedBy (heuristique) → mapping potentiellement incorrect.",
                "suggested_safe_fix": "Vérifier association bidirectionnelle et ajouter mappedBy si approprié."
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
