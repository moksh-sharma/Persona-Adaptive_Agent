# Persona Support Agent

A **KB-grounded support chatbot** prototype for an AI Intern assignment: it retrieves relevant in-memory Help Center articles (often several at once), routes tone using **keyword-only personas**, optionally calls **Ollama** (`/api/chat`) to elaborate answers while staying anchored to KB facts, then **falls back cleanly** to rule templates if the LLM is off or errors.

---

## Problem statement

Support requests arrive in wildly different voices: engineers want precise diagnostics and API-level guidance, distressed users need empathy and reassurance, executives need SLA and operational risk framing, while general consumers need simplicity. Routing all of those through one flat script produces poor experiences and hides cases that merit human escalation.

This project wires **persona inference (rules)** - KB retrieval + context packing - escalation policy - **chat completion** optional via Ollama - so demos work offline while still showcasing local LLMs when configured.

---

## Features

| Capability | Detail |
|-----------|--------|
| **Persona routing** | `Technical Expert`, `Frustrated User`, `Business Executive`, `General User` via tiered keywords only (no LLM). Priority: frustrated - business - technical - general. |
| **KB retrieval** | 16 curated in-memory articles + **General Support** fallback; top matches are fused into prompt context / rule fallback copy. |
| **Chatbot replies** | `chatbot.py` drives **Ollama `/api/chat`** with system instructions + persona tone + pasted KB excerpts. |
| **Escalation & handoff** | Rule engine yields `human_handoff_context` for risky phrasing/personas. |
| **Optional Ollama** | Persona/KB retrieval never needs the network; enabling `LLM_PROVIDER=ollama` lets the assistant expand answers grounded in KB. |
| **Interactive API docs** | Swagger UI at `/docs`. |
| **Web UI** | Original **support** form (`POST /support`), plus floating **Tool Guide** (`POST /tool-chat`, Ollama only). Multi-turn support still available via `POST /chat`. |

---

## Architecture (text diagram)

```
┌----------------------┐
│  Client (React UI)   │
│  or HTTP / Swagger   │
└----------┬-----------┘
           │ POST /chat { messages[] }  (or POST /support single-turn)
           ▼
┌----------------------┐
│ persona_detector     │  keyword-only persona (no Ollama)
└----------┬-----------┘
           │ persona
           ▼
┌----------------------┐
│ kb_retriever         │  scored articles - top excerpts for context
└----------┬-----------┘
           │ KB blocks
           ▼
┌----------------------┐
│ escalation_engine    │  policy - required? + handoff_context
└----------┬-----------┘
           │
           ▼
┌----------------------┐     optional       ┌----------------------┐
│ chatbot.run_chat_turn│ ---- Ollama chat   │ llm_service          │
│ + response_generator │ ◀----------------- │ call_ollama_chat()   │
│   (rule fallback)    │                    │ /api/chat            │
└----------┬-----------┘                    └----------------------┘
           │
           ▼
     JSON response to client
```

---

## Tech stack

- **Backend:** Python 3, FastAPI, Uvicorn, Pydantic, `python-dotenv`, `requests`
- **Frontend:** React 18 + Vite
- **LLM (optional):** Ollama HTTP API (`/api/chat` for turns; `/api/generate` helper still available)

**Security note:** This repository intentionally contains **no API keys** and **no bundled model weights**. Ollama model files are large runtime dependencies and are **not** checked in.

---

## Folder structure

```
persona-support-agent/
├-- backend/
│   ├-- main.py
│   ├-- persona_detector.py
│   ├-- kb_articles.py
│   ├-- kb_retriever.py
│   ├-- response_generator.py
│   ├-- chatbot.py
│   ├-- tool_guide.py
│   ├-- escalation_engine.py
│   ├-- llm_service.py
│   ├-- requirements.txt
│   └-- .env.example
├-- frontend/
│   ├-- package.json
│   ├-- vite.config.js
│   ├-- index.html
│   ├-- .env.example
│   └-- src/
│       ├-- main.jsx
│       ├-- App.jsx
│       ├-- App.css
│       └-- index.css
├-- README.md
└-- sample_outputs.md
```

---

## Setup

### Prerequisites

- Python **3.10+** recommended
- **Node.js 18+** (for the React UI)
- **Optional:** [Ollama](https://ollama.com) installed locally if you want LLM-backed steps

### Backend environment

```bash
cd backend
cp .env.example .env   # optional; edit LLM_PROVIDER if using Ollama
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend environment

```bash
cd frontend
npm install
# optional: cp .env.example .env.local  # set VITE_API_URL if backend is not on 127.0.0.1:8000
```

---

## Run the backend

```bash
cd backend
source .venv/bin/activate   # if using a venv
uvicorn main:app --reload
```

- **API base:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health:** `GET /health`
- **Docs shortcut:** `GET /` redirects to `/docs`

---

## Run the frontend

With the backend already running:

```bash
cd frontend
npm run dev
```

Open the printed local URL (defaults to Vite’s `http://localhost:5173`). The main page calls **`POST /support`** unless `VITE_API_URL` overrides the host; the floating **?** launcher calls **`POST /tool-chat`** (Ollama only).

---

## API

### `POST /tool-chat` (project helper, **Ollama only**, **no KB**)

Answers questions **about this repository** (how to run, env vars, routes). Requires `LLM_PROVIDER=ollama` and a reachable model; otherwise returns **503**.

**Request** - same envelope as `/chat`:

```json
{
  "messages": [{ "role": "user", "content": "How do I start the backend?" }]
}
```

**Response**

```json
{ "message": { "role": "assistant", "content": "..." } }
```

### `POST /chat` (KB-grounded support, multi-turn)

Multi-turn chat. Body is an ordered transcript ending with a **user** message.

**Request**

```json
{
  "messages": [
    { "role": "user", "content": "First question..." },
    { "role": "assistant", "content": "..." },
    { "role": "user", "content": "Follow-up..." }
  ]
}
```

**Response (high level)**

- `message`: `{ "role": "assistant", "content": "..." }`
- `detected_persona`, `retrieved_kb` (primary hit), `retrieved_kb_articles` (all excerpts passed to the model/fallback)
- `escalation_required`, `human_handoff_context`, `llm_used`

### `POST /support` (**primary demo UI**, single-turn)

Same KB + escalation + optional-Ollama engine as `/chat`, with:

```json
{ "customer_query": "string" }
```

Response adds `response` (assistant text) plus `retrieved_kb_articles` and `llm_used`.

- `human_handoff_context` is **`null`** when `escalation_required` is `false`.

### Example `curl`

```bash
curl -s http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Our API returns 401 even with a fresh bearer token."}]}' | jq
```

More payloads live in [`sample_outputs.md`](sample_outputs.md).

---

## Ollama integration

1. Pull a model (example from `.env.example`):

   ```bash
   ollama pull llama3.2
   ```

2. Start the server (usually automatic when using the Ollama app; otherwise `ollama serve`).

3. Configure the backend:

   ```bash
   # backend/.env
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2
   ```

4. Restart Uvicorn.

Grounded replies use **`llm_service.call_ollama_chat`**, posting to:

`POST {OLLAMA_BASE_URL}/api/chat`

```json
{
  "model": "llama3.2",
  "messages": [
    { "role": "system", "content": "... KB excerpts + persona/tone hints ..." },
    { "role": "user", "content": "..." }
  ],
  "stream": false
}
```

`call_ollama` (`/api/generate`) remains for simple one-off prompts during development.

Errors, timeouts, or empty bodies are swallowed so the assistant **drops to rule templates** that still weave in KB text.

---

## Fallback behavior (no Ollama)

With `LLM_PROVIDER` unset, `none`, or anything other than `ollama`:

- **Persona detection** uses tiered keyword rules (frustrated - business - technical - general).
- **Responses** come from persona-specific templates in `response_generator.py` using the highest-ranked KB article (plus escalation hints).
- **Escalation** remains fully deterministic.

This guarantees the assignment demo works on any machine without downloading multi-gigabyte weights.

---

## Future improvements

- Persistent vector KB (e.g., embeddings + metadata filters) while keeping explainable retrieval.
- Confidence scores for persona + retrieval to drive clarifying questions instead of instant answers.
- Authentication and rate limiting for production deployment.
- Streaming responses and Server-Sent Events for a more chat-native UX.
- Observability: structured logs, trace IDs, and evaluation sets for regression testing.

---

## Assignment Completion Summary

This project implements a Persona-Adaptive Customer Support Agent that detects customer persona, retrieves relevant knowledge base content, adapts response tone, and escalates high-risk cases to a human agent with structured context handoff. The system supports optional Ollama-based LLM reasoning and includes a rule-based fallback to ensure reliable execution in any environment.
