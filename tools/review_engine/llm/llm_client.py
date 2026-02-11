import json
import urllib.request
import urllib.error

from ..exceptions import LLMError


def ollama_generate(model: str, prompt: str) -> str:
    """
    Call Ollama using HTTP API to avoid ANSI/TTY artifacts from CLI.
    Returns the model raw response text.
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=600) as resp:
            body = resp.read().decode("utf-8", errors="replace")

        data = json.loads(body)
        out = (data.get("response") or "").strip()

        if not out:
            raise LLMError("Empty LLM output")

        return out

    except urllib.error.HTTPError as e:
        try:
            details = e.read().decode("utf-8", errors="replace")
        except Exception:
            details = ""
        raise LLMError(f"Ollama HTTP error: {e.code} {e.reason} {details}") from e

    except Exception as e:
        raise LLMError(f"Ollama call failed: {e}") from e
