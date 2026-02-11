from pathlib import Path

REST_ANN = ("@RestController", "@Controller")
MAPPING_ANN = ("@RequestMapping", "@GetMapping", "@PostMapping", "@PutMapping", "@DeleteMapping", "@PatchMapping")

def analyze_spring(context: dict) -> list[dict]:
    findings = []
    idx = context.get("repo_index", {})
    controllers = idx.get("controllers", [])
    services = set(idx.get("services", []))
    repos = set(idx.get("repositories", []))
    advice = idx.get("advice", [])

    for fp in controllers:
        p = Path(fp)
        if not p.exists():
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")

        # Controller -> Repository direct (heuristic)
        if "Repository" in txt and ("@Autowired" in txt or "private final" in txt):
            findings.append({
                "priority": "P1",
                "topic": "layering",
                "file": fp,
                "message": "Controller semble dépendre d'un Repository (risque violation layering).",
                "suggested_safe_fix": "Introduire/Utiliser un Service intermédiaire (sans changer endpoints)."
            })

        # @RequestBody without @Valid
        if "@RequestBody" in txt and "@Valid" not in txt:
            findings.append({
                "priority": "P2",
                "topic": "dto",
                "file": fp,
                "message": "@RequestBody sans @Valid → validation DTO potentiellement manquante.",
                "suggested_safe_fix": "Ajouter @Valid sur le paramètre DTO + contraintes Bean Validation sur DTO."
            })

        # Optional.get risk in controller
        if ".findById(" in txt and ".get()" in txt:
            findings.append({
                "priority": "P1",
                "topic": "error",
                "file": fp,
                "message": "Usage probable de Optional.get() → risque NoSuchElementException (500).",
                "suggested_safe_fix": "Remplacer par orElseThrow + ResponseStatusException(HttpStatus.NOT_FOUND,...)."
            })

        # Missing controller advice
        if not advice:
            findings.append({
                "priority": "P2",
                "topic": "error",
                "file": fp,
                "message": "Aucun @ControllerAdvice détecté (gestion d'erreurs centralisée potentiellement absente).",
                "suggested_safe_fix": "Ajouter un GlobalExceptionHandler minimal si le projet n'en a pas."
            })

        # Entity leak heuristic: endpoints returning entity directly (rough)
        if any(a in txt for a in MAPPING_ANN) and "Dto" not in txt and "DTO" not in txt:
            # too heuristic; keep as low priority
            findings.append({
                "priority": "P2",
                "topic": "dto",
                "file": fp,
                "message": "Contrat REST pourrait exposer Entity (heuristique).",
                "suggested_safe_fix": "Si DTO existe déjà, retourner DTO côté controller, mapping dans service."
            })

    # Service/repo sanity: ensure services exist if repos are used
    if repos and not services:
        findings.append({
            "priority": "P2",
            "topic": "layering",
            "file": "-",
            "message": "Repositories détectés sans Services détectés (architecture potentiellement plate).",
            "suggested_safe_fix": "Ajouter/structurer layer Service pour logique métier (refactor progressif)."
        })

    return _dedupe(findings)

def _dedupe(findings: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for f in findings:
        k = (f.get("priority"), f.get("topic"), f.get("file"), f.get("message"))
        if k in seen:
            continue
        seen.add(k)
        out.append(f)
    return out
