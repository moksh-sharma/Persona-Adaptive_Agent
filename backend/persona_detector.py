"""
Rule-based persona detection (keyword tiers).
Priority: Frustrated User > Business Executive > Technical Expert > General User
"""

from __future__ import annotations

TECHNICAL_KEYWORDS = (
    "api",
    "endpoint",
    "server",
    "logs",
    "payload",
    "database",
    "latency",
    "token",
    "authentication",
    "error code",
    "integration",
    "webhook",
    "request",
    "response",
)

FRUSTRATED_KEYWORDS = (
    "angry",
    "frustrated",
    "not working",
    "terrible",
    "bad experience",
    "still not fixed",
    "urgent",
    "waste",
    "disappointed",
    "annoying",
    "irritated",
    "useless",
)

BUSINESS_KEYWORDS = (
    "sla",
    "revenue",
    "downtime",
    "business impact",
    "client impact",
    "roi",
    "productivity",
    "loss",
    "management",
    "executive",
    "contract",
    "customer churn",
)


def _normalize(query: str) -> str:
    return query.strip().lower()


def detect_persona(query: str) -> str:
    """
    Classify customer persona from the latest user text only (no LLM).

    Keyword priority: frustrated > business > technical > general.
    """
    q = _normalize(query)
    for kw in FRUSTRATED_KEYWORDS:
        if kw in q:
            return "Frustrated User"
    for kw in BUSINESS_KEYWORDS:
        if kw in q:
            return "Business Executive"
    for kw in TECHNICAL_KEYWORDS:
        if kw in q:
            return "Technical Expert"
    return "General User"
