"""
Escalation rules for human handoff with structured context.
"""

from __future__ import annotations

import re
from typing import Any


_AGENT_MANAGER_RE = re.compile(r"\b(agent|manager)\b", re.IGNORECASE)
_HUMAN_RE = re.compile(
    r"(human\s+agent|talk\s+to\s+a?\s*human|speak\s+to\s+a?\s*human|real\s+person|human\s+support)",
    re.IGNORECASE,
)


def should_escalate(query: str, persona: str, kb_result: dict[str, Any]) -> dict[str, Any]:
    """
    Determine if human escalation is needed and assemble handoff payload.

    kb_result expects keys title and content.
    """
    q = query.strip().lower()
    reasons: list[str] = []
    recommended_actions: list[str] = []

    def add(reason: str, action: str) -> None:
        if reason not in reasons:
            reasons.append(reason)
        if action not in recommended_actions:
            recommended_actions.append(action)

    if persona == "Frustrated User":
        add(
            "Customer expresses strong frustration.",
            "Assign to a senior agent for empathetic outreach and prioritized follow-up.",
        )

    plain = query.strip()
    if _HUMAN_RE.search(plain) or _AGENT_MANAGER_RE.search(plain):
        add(
            "Customer explicitly requested a human, agent, or manager.",
            "Warm transfer with transcript, KB excerpt, persona, and any SLA/account flags.",
        )

    high_risk = (
        ("refund", "Billing or refund decision may require human approval."),
        ("legal", "Route to Legal review."),
        ("lawsuit", "Immediate Legal and executive on-call escalation."),
        ("compliance", "Engage Compliance / GRC."),
        ("cancel", "Cancellation may impact contract obligations - human verification recommended."),
    )
    for word, rationale in high_risk:
        if word in q:
            add(rationale, "Preserve written record and route to owning team.")

    escalation_phrases = ("not resolved", "urgent", "critical")
    for phrase in escalation_phrases:
        if phrase in q:
            add(
                f"Detected escalation phrase '{phrase}'.",
                "Incident-style handling with proactive stakeholder updates.",
            )

    sla_business = (
        ("sla", "SLA-sensitive language - verify contractual commitments."),
        ("revenue loss", "Potential revenue impact - investigate with account leadership."),
        ("client impact", "Downstream customer impact - increase priority."),
        ("contract risk", "Contractual exposure - coordinate with account/legal."),
    )
    for phrase, rationale in sla_business:
        if phrase in q:
            add(rationale, "Align on mitigation plan, ETA, and customer comms.")

    repetition = (
        "again",
        "multiple times",
        "happened twice",
        "still happening",
        "repeated issue",
        "persistent",
        "keeps failing",
        "still broken",
        "yet again",
    )
    if any(term in q for term in repetition):
        add(
            "Possible recurring or persistent issue.",
            "Open triage with engineering context and offer interim workaround if available.",
        )

    required = len(reasons) > 0
    reason_text = "; ".join(reasons) if reasons else ""
    recommended = (
        "; ".join(recommended_actions)
        if recommended_actions
        else "Continue automation with monitoring."
    )

    handoff_context: dict[str, Any] | None = None
    if required:
        handoff_context = {
            "persona": persona,
            "issue_summary": query.strip(),
            "retrieved_kb_title": kb_result.get("title", "Unknown"),
            "reason": reason_text,
            "recommended_action": recommended,
        }

    return {"required": required, "handoff_context": handoff_context}
