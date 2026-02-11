def spring_safe_hints() -> dict:
    return {
        "optional": "Prefer orElseThrow + ResponseStatusException (404/400) instead of Optional.get().",
        "validation": "Use @Valid on @RequestBody DTO, add Bean Validation annotations on DTO fields.",
        "layering": "Keep Controller -> Service -> Repository, no repo access from controller.",
        "errors": "Prefer centralized handler (@ControllerAdvice) or ResponseStatusException; avoid swallowing exceptions.",
        "refactor": "Extract private methods, reduce nested ifs, early returns/guard clauses, remove duplication."
    }
