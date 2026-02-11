from __future__ import annotations
import requests
from typing import Any
from .config import Config

class LLMError(RuntimeError):
    pass

def call_llm(cfg: Config, messages: list[dict[str,str]]) -> str:
    provider = (cfg.llm_provider or "openai_compatible").strip().lower()

    if provider == "openai_compatible":
        if not cfg.llm_base_url:
            raise LLMError("LLM_BASE_URL missing for openai_compatible.")
        url = cfg.llm_base_url.rstrip("/") + "/v1/chat/completions"
        payload: dict[str, Any] = {
            "model": cfg.llm_model,
            "messages": messages,
            "temperature": cfg.llm_temperature,
            "max_tokens": cfg.llm_max_tokens,
        }
        headers = {"Authorization": f"Bearer {cfg.llm_api_key}", "Content-Type":"application/json"}
        r = requests.post(url, json=payload, headers=headers, timeout=cfg.llm_timeout_sec)
        if r.status_code >= 400:
            raise LLMError(f"LLM HTTP {r.status_code}: {r.text[:900]}")
        data = r.json()
        return data["choices"][0]["message"]["content"]

    if provider == "ollama":
        if not cfg.ollama_base_url:
            raise LLMError("OLLAMA_BASE_URL missing for ollama.")
        url = cfg.ollama_base_url.rstrip("/") + "/api/chat"
        payload = {"model": cfg.ollama_model, "messages": messages, "stream": False, "options": {"temperature": cfg.llm_temperature}}
        r = requests.post(url, json=payload, timeout=cfg.llm_timeout_sec)
        if r.status_code >= 400:
            raise LLMError(f"Ollama HTTP {r.status_code}: {r.text[:900]}")
        data = r.json()
        return data["message"]["content"]

    raise LLMError(f"Unknown LLM_PROVIDER: {cfg.llm_provider}")
