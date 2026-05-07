"""
Keyword-based retrieval over the shared knowledge base in `kb_articles`.
"""

from __future__ import annotations

from kb_articles import KBEntry, KNOWLEDGE_BASE

GENERAL_ARTICLE = KNOWLEDGE_BASE[-1]
_NON_GENERAL = KNOWLEDGE_BASE[:-1]


def _score_entry(q: str, entry: KBEntry) -> int:
    return sum(1 for kw in entry["keywords"] if kw.lower() in q)


def retrieve_kb_candidates(query: str, max_articles: int = 4) -> list[dict[str, str]]:
    """
    Return ranked KB excerpts for RAG-style prompts: top-scoring articles (up to max_articles),
    or General Support when nothing matches.
    """
    q = query.strip().lower()
    ranked: list[tuple[int, KBEntry]] = sorted(
        ((_score_entry(q, e), e) for e in _NON_GENERAL),
        key=lambda t: t[0],
        reverse=True,
    )
    top_score = ranked[0][0] if ranked else 0
    if top_score == 0:
        return [
            {"title": GENERAL_ARTICLE["title"], "content": GENERAL_ARTICLE["content"]},
        ]
    out: list[dict[str, str]] = []
    for score, entry in ranked:
        if score == 0 or len(out) >= max_articles:
            break
        if score >= max(1, top_score - 1):
            out.append({"title": entry["title"], "content": entry["content"]})
    return out[:max_articles]


def retrieve_kb(query: str) -> dict[str, str]:
    """
    Best single KB article by keyword hits (backwards-compatible).
    """
    candidates = retrieve_kb_candidates(query, max_articles=1)
    return {"title": candidates[0]["title"], "content": candidates[0]["content"]}


def kb_context_block(candidates: list[dict[str, str]]) -> str:
    """Format multiple articles for injection into chat prompts."""
    parts = []
    for block in candidates:
        parts.append(f"### {block['title']}\n{block['content']}")
    return "\n\n".join(parts)
