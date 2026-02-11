def sonar_recheck_stub(logger) -> dict:
    """
    Enterprise pipelines may re-run sonar scan and compare.
    Livrable: stub (ne bloque pas).
    """
    logger.info("Sonar recheck skipped (stub).")
    return {"performed": False, "reason": "stub"}
