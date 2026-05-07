"""
Ollama-only assistant that answers questions about the persona-support-agent project itself.

No customer-support KB is used - only general project facts in the system prompt.
"""

from __future__ import annotations

from llm_service import call_ollama_chat, is_llm_enabled

TOOL_GUIDE_SYSTEM_PROMPT = """You are **Tool Guide**, a concise helper embedded in the local demo repo `persona-support-agent`.

Audience: developers running this assignment/demo on their machine.

You MUST:
- Explain how THIS project runs: backend (FastAPI, Uvicorn), frontend (React + Vite), env vars, Swagger at /docs.
- Describe API routes: POST /support (single customer query, KB-grounded persona support), POST /chat (multi-turn KB-grounded), POST /tool-chat (this assistant - project help only via Ollama, no KB).
- Mention persona detection is keyword-only; customer answers use KB + optional Ollama /api/chat; this tool-chat uses Ollama only.
- Mention LLM_PROVIDER=ollama, OLLAMA_BASE_URL, OLLAMA_MODEL in backend .env.example.
- Mention `ollama pull` + `ollama serve` when they ask how to enable the model.

You MUST NOT:
- Pretend to retrieve Help Center KB articles when answering ABOUT the project (no fake KB excerpts).
- Diagnose hypothetical customer outages as if KB content were loaded, unless they are explicitly testing UX copy.

Reply in short paragraphs or brief bullets; stay accurate."""


def run_tool_guide_chat(messages: list[dict[str, str]]) -> tuple[str | None, str | None]:
    """
    Returns (assistant_text, error_detail).
    error_detail set when LLM unavailable or produces empty output.
    """
    if not is_llm_enabled():
        return (
            None,
            "Ollama is not enabled. Set LLM_PROVIDER=ollama in backend/.env and restart Uvicorn (see README).",
        )

    ollama_messages: list[dict[str, str]] = [{"role": "system", "content": TOOL_GUIDE_SYSTEM_PROMPT}]
    for m in messages:
        if m.get("role") in ("user", "assistant") and (m.get("content") or "").strip():
            ollama_messages.append({"role": m["role"], "content": m["content"].strip()})

    text = call_ollama_chat(ollama_messages).strip()
    if not text:
        return (
            None,
            "Ollama returned an empty reply. Confirm `ollama serve` is running and the model from OLLAMA_MODEL is pulled.",
        )
    return text, None
