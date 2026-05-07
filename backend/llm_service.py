"""
Optional Ollama integration for chat completions (KB-grounded replies).

No API keys are used. Set LLM_PROVIDER=ollama and run `ollama serve` with your model pulled.
"""

import json
import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "none").lower().strip()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def call_ollama(prompt: str) -> str:
    """Call local Ollama /api/generate (non-streaming). Returns assistant text or empty string on failure."""
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload: dict[str, Any] = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        text = data.get("response") or ""
        return str(text).strip()
    except (requests.RequestException, json.JSONDecodeError, ValueError):
        return ""


def call_ollama_chat(messages: list[dict[str, str]]) -> str:
    """
    Multi-turn chat via POST /api/chat (non-streaming).
    Each message: {"role": "system"|"user"|"assistant", "content": "..."}
    """
    url = f"{OLLAMA_BASE_URL}/api/chat"
    payload: dict[str, Any] = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
    }
    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        msg = data.get("message") or {}
        text = msg.get("content") or ""
        return str(text).strip()
    except (requests.RequestException, json.JSONDecodeError, ValueError, TypeError):
        return ""


def call_llm(prompt: str) -> str:
    """Single-string generation (legacy /api/generate)."""
    if LLM_PROVIDER != "ollama":
        return ""
    return call_ollama(prompt)


def is_llm_enabled() -> bool:
    return LLM_PROVIDER == "ollama"
