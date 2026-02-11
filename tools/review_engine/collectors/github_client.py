class GitHubClient:
    """
    Optionnel (enterprise): PR metadata / comments.
    Version livrable: stub propre (n'empêche jamais l'exécution).
    """
    def __init__(self, token: str | None = None):
        self.token = token

    def enabled(self) -> bool:
        return False

    def post_comment(self, message: str) -> None:
        # no-op
        return
