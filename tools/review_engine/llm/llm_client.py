import subprocess
from ..exceptions import LLMError

def ollama_generate(model: str, prompt: str) -> str:
    try:
        p = subprocess.run(
            ["ollama", "run", model],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False
        )
        out = p.stdout.decode("utf-8", errors="replace")
        if not out.strip():
            raise LLMError("Empty LLM output")
        return out
    except Exception as e:
        raise LLMError(f"Ollama call failed: {e}") from e
