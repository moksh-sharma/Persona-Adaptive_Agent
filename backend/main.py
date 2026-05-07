"""
FastAPI app: persona routing (keywords), KB-backed replies with optional Ollama, and a separate tool-guide endpoint.
"""

from __future__ import annotations

from typing import Any, Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from chatbot import kb_for_query, kb_query_from_messages, last_user_text, run_chat_turn
from escalation_engine import should_escalate
from persona_detector import detect_persona
from tool_guide import run_tool_guide_chat

load_dotenv()

app = FastAPI(
    title="Persona Support Agent API",
    description="Customer support: KB + optional Ollama (/support, /chat). Floating UI tool guide: Ollama-only /tool-chat (no KB).",
    version="2.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., min_length=1)


class AssistantPayload(BaseModel):
    role: Literal["assistant"] = "assistant"
    content: str


class RetrievedKB(BaseModel):
    title: str
    content: str


class ChatResponse(BaseModel):
    message: AssistantPayload
    detected_persona: str
    retrieved_kb: RetrievedKB
    retrieved_kb_articles: list[RetrievedKB]
    escalation_required: bool
    human_handoff_context: dict[str, Any] | None = None
    llm_used: bool


class SupportRequest(BaseModel):
    customer_query: str = Field(..., min_length=1, description="The customer's question or complaint.")


class SupportResponse(BaseModel):
    detected_persona: str
    retrieved_kb: RetrievedKB
    retrieved_kb_articles: list[RetrievedKB]
    escalation_required: bool
    human_handoff_context: dict[str, Any] | None = None
    response: str
    llm_used: bool


class ToolChatResponse(BaseModel):
    """Project help assistant (Ollama only; no KB)."""

    message: AssistantPayload


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    """Convenience redirect to interactive API docs."""
    return RedirectResponse(url="/docs")


def _run_pipeline(messages: list[dict[str, str]]) -> ChatResponse:
    if not messages or messages[-1].get("role") != "user":
        raise HTTPException(status_code=400, detail="Last message must be from the user.")

    utterance = last_user_text(messages)
    if not utterance:
        raise HTTPException(status_code=400, detail="Empty user message.")

    persona = detect_persona(utterance)
    kb_candidates = kb_for_query(kb_query_from_messages(messages))
    primary = kb_candidates[0]
    escalation_result = should_escalate(utterance, persona, primary)
    escalation_block = {
        "required": escalation_result["required"],
        "handoff_context": escalation_result.get("handoff_context"),
    }

    reply, llm_used = run_chat_turn(
        messages,
        persona=persona,
        kb_candidates=kb_candidates,
        escalation=escalation_block,
    )

    articles = [RetrievedKB(title=a["title"], content=a["content"]) for a in kb_candidates]

    return ChatResponse(
        message=AssistantPayload(content=reply),
        detected_persona=persona,
        retrieved_kb=RetrievedKB(title=primary["title"], content=primary["content"]),
        retrieved_kb_articles=articles,
        escalation_required=bool(escalation_result["required"]),
        human_handoff_context=escalation_result.get("handoff_context"),
        llm_used=llm_used,
    )


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """Multi-turn chat: KB retrieval + optional Ollama chat completion."""
    raw = [m.model_dump() for m in req.messages]
    return _run_pipeline(raw)


@app.post("/tool-chat", response_model=ToolChatResponse)
def tool_chat(req: ChatRequest) -> ToolChatResponse:
    """
    Ollama-only chat about THIS repository (setup, APIs, architecture).
    Does not consult the customer-support knowledge base.
    """
    raw = [m.model_dump() for m in req.messages]
    if not raw or raw[-1].get("role") != "user":
        raise HTTPException(status_code=400, detail="Last message must be from the user.")
    reply, err = run_tool_guide_chat(raw)
    if err or reply is None:
        raise HTTPException(status_code=503, detail=err or "Tool assistant unavailable.")
    return ToolChatResponse(message=AssistantPayload(content=reply))


@app.post("/support", response_model=SupportResponse)
def support(req: SupportRequest) -> SupportResponse:
    """Single-turn alias: one user message, same engine as /chat."""
    result = _run_pipeline([{"role": "user", "content": req.customer_query.strip()}])
    return SupportResponse(
        detected_persona=result.detected_persona,
        retrieved_kb=result.retrieved_kb,
        retrieved_kb_articles=result.retrieved_kb_articles,
        escalation_required=result.escalation_required,
        human_handoff_context=result.human_handoff_context,
        response=result.message.content,
        llm_used=result.llm_used,
    )
