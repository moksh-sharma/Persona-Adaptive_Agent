"""
KB-grounded chatbot: Ollama chat API with persona-aware tone and rule-based fallback.
"""

from __future__ import annotations

from typing import Any

from kb_retriever import kb_context_block, retrieve_kb_candidates
from llm_service import call_ollama_chat, is_llm_enabled

from response_generator import generate_rule_based_reply


def _system_prompt(persona: str, kb_excerpts: str, escalation: dict[str, Any]) -> str:
    esc_note = ""
    if escalation.get("required"):
        hc = escalation.get("handoff_context") or {}
        esc_note = (
            "A human handoff is recommended. Briefly tell the user a teammate will follow up. "
            f"Internal context (do not read verbatim): {hc.get('reason', '')}"
        )
    return (
        "You are a customer support chatbot for an enterprise SaaS product.\n"
        "Use ONLY the knowledge base excerpts below as factual sources. If they do not cover the question, "
        "say so honestly and suggest contacting support or a human agent.\n"
        "Do not invent policy, pricing, or guarantees.\n\n"
        f"Knowledge base:\n{kb_excerpts}\n\n"
        f"Detected customer style (adapt tone, do not name the label): {persona}\n"
        "- Technical Expert: direct, technical; mention logs, configuration, API behavior where relevant.\n"
        "- Frustrated User: empathetic, calm, short clear steps.\n"
        "- Business Executive: concise, professional; mention priority, risk, resolution path.\n"
        "- General User: simple, friendly language.\n"
        f"{esc_note}\n"
        "Reply to the user's latest message. Be concise."
    )


def run_chat_turn(
    messages: list[dict[str, str]],
    *,
    persona: str,
    kb_candidates: list[dict[str, str]],
    escalation: dict[str, Any],
) -> tuple[str, bool]:
    """
    Produce assistant reply. Returns (text, llm_used).
    """
    kb_excerpts = kb_context_block(kb_candidates)
    last_user = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            last_user = m.get("content") or ""
            break

    if is_llm_enabled():
        ollama_messages: list[dict[str, str]] = [
            {"role": "system", "content": _system_prompt(persona, kb_excerpts, escalation)},
        ]
        for m in messages:
            if m.get("role") in ("user", "assistant"):
                ollama_messages.append({"role": m["role"], "content": m["content"]})
        reply = call_ollama_chat(ollama_messages)
        if reply:
            return reply, True

    primary = kb_candidates[0] if kb_candidates else {"title": "General Support", "content": ""}
    fallback = generate_rule_based_reply(last_user, persona, primary["content"], escalation)
    return fallback, False


def last_user_text(messages: list[dict[str, str]]) -> str:
    for m in reversed(messages):
        if m.get("role") == "user":
            return (m.get("content") or "").strip()
    return ""


def kb_query_from_messages(messages: list[dict[str, str]]) -> str:
    """Blend recent user turns so short follow-ups still inherit topical keywords."""
    user_parts = [
        (m.get("content") or "").strip()
        for m in messages
        if m.get("role") == "user" and (m.get("content") or "").strip()
    ]
    if not user_parts:
        return ""
    if len(user_parts) >= 2:
        return f"{user_parts[-2]} {user_parts[-1]}"
    return user_parts[-1]


def kb_for_query(user_text: str) -> list[dict[str, str]]:
    """Retrieve KB articles for grounding."""
    return retrieve_kb_candidates(user_text, max_articles=4)
