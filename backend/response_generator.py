"""
Rule-based replies when Ollama is disabled or unreachable.
(Chat layer calls these after KB retrieval.)
"""

from __future__ import annotations

from typing import Any


def generate_rule_based_reply(query: str, persona: str, kb_content: str, escalation: dict[str, Any]) -> str:
    esc_line = ""
    if escalation.get("required"):
        esc_line = (
            " I've flagged this for a human specialist using the handoff summary so you are not left waiting "
            "without ownership."
        )

    if persona == "Technical Expert":
        return (
            f"Thanks for the detail. Based on our KB: {kb_content} "
            f"Next checks: pull recent request/response pairs and edge logs, verify auth headers and token TTL, "
            f"confirm environment + permissions, and capture correlation IDs for any failing calls.{esc_line}"
        )

    if persona == "Frustrated User":
        return (
            "I'm sorry this has been stressful - I'll walk this with you calmly. "
            f"Here is what we know from our guides: "
            f"{kb_content} "
            "Let's go step by step: try the first fix, tell me the exact error or screen you see, "
            "and we'll adjust. You're not alone on this."
            f"{esc_line}"
        )

    if persona == "Business Executive":
        return (
            "Executive summary: we've matched your report to our operational guidance. "
            f"{kb_content} "
            "From a business standpoint, we will prioritize stability, SLA exposure, and a clear resolution path "
            "with owners and ETAs. "
            f"I can provide a concise incident note for leadership if needed.{esc_line}"
        )

    return (
        "Thanks for reaching out. "
        f"Here's a simple explanation based on what we recommend: {kb_content} "
        "If anything is unclear, tell me where you're stuck (for example during login or payment) "
        "and I'll simplify the next steps."
        f"{esc_line}"
    )
