from __future__ import annotations

import os
import requests
from typing import Any
from .config import Config


class LLMError(RuntimeError):
    pass


def _messages_to_prompt_text(messages: list[dict[str, str]]) -> str:
    """
    Convertit le format OpenAI-like (role/content) en texte unique.
    Fonctionne bien pour Gemini sans dépendre d'un format 'contents' multi-turn.
    """
    chunks: list[str] = []
    for m in messages:
        role = (m.get("role") or "user").strip().upper()
        content = (m.get("content") or "").strip()
        if not content:
            continue
        chunks.append(f"{role}:\n{content}")
    return "\n\n".join(chunks).strip()


def call_llm(cfg: Config, messages: list[dict[str, str]]) -> str:
    provider = (cfg.llm_provider or "openai_compatible").strip().lower()

    # ---------------------------
    # 1) OpenAI-compatible
    # ---------------------------
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
        headers = {
            "Authorization": f"Bearer {cfg.llm_api_key}",
            "Content-Type": "application/json",
        }
        r = requests.post(url, json=payload, headers=headers, timeout=cfg.llm_timeout_sec)
        if r.status_code >= 400:
            raise LLMError(f"LLM HTTP {r.status_code}: {r.text[:900]}")
        data = r.json()
        return data["choices"][0]["message"]["content"]

    # ---------------------------
    # 2) Ollama
    # ---------------------------
    if provider == "ollama":
        if not cfg.ollama_base_url:
            raise LLMError("OLLAMA_BASE_URL missing for ollama.")
        url = cfg.ollama_base_url.rstrip("/") + "/api/chat"
        payload = {
            "model": cfg.ollama_model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": cfg.llm_temperature},
        }
        r = requests.post(url, json=payload, timeout=cfg.llm_timeout_sec)
        if r.status_code >= 400:
            raise LLMError(f"Ollama HTTP {r.status_code}: {r.text[:900]}")
        data = r.json()
        return data["message"]["content"]

    # ---------------------------
    # 3) Gemini (Google)
    # ---------------------------
    if provider == "gemini":
        # clé: soit LLM_API_KEY (cfg.llm_api_key), soit GEMINI_API_KEY en env
        api_key = (cfg.llm_api_key or "").strip() or (os.getenv("GEMINI_API_KEY") or "").strip()
        if not api_key:
            raise LLMError("GEMINI_API_KEY missing (or set LLM_API_KEY).")

        model = (os.getenv("GEMINI_MODEL") or "gemini-flash-latest").strip()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

        prompt_text = _messages_to_prompt_text(messages)
        if not prompt_text:
            raise LLMError("Gemini: empty prompt built from messages.")

        # Format Gemini: contents -> parts -> text
        payload: dict[str, Any] = {
            "contents": [
                {"role": "user", "parts": [{"text": prompt_text}]}
            ]
        }

        headers = {"x-goog-api-key": api_key, "Content-Type": "application/json"}
        r = requests.post(url, json=payload, headers=headers, timeout=cfg.llm_timeout_sec)

        if r.status_code >= 400:
            raise LLMError(f"Gemini HTTP {r.status_code}: {r.text[:900]}")

        data = r.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            raise LLMError(f"Gemini unexpected response: {str(data)[:900]}")

    raise LLMError(f"Unknown LLM_PROVIDER: {cfg.llm_provider}")
