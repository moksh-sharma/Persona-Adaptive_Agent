# Sample API outputs

Examples below assume **`LLM_PROVIDER=none`** (rule-based replies, `llm_used: false`). Enable Ollama to get natural language from `/api/chat`; the JSON shape is unchanged and `llm_used` flips to **`true`** when the model returns content.

---

## 1. Technical Expert - API 401 issue (`POST /support`)

**Request**

```http
POST /support HTTP/1.1
Content-Type: application/json

{
  "customer_query": "Our integration is returning HTTP 401 on POST https://api.example.com/v2/events. We send the Bearer token generated from the OAuth app. Can you point us to scopes or clock-skew expectations?"
}
```

**Response (truncated `response` text)**

```json
{
  "detected_persona": "Technical Expert",
  "retrieved_kb": {
    "title": "API Authentication Error",
    "content": "For API authentication errors (e.g., 401/403): verify API keys/scopes have not rotated, check expiry and clock skew, confirm you send the Authorization header/OAuth bearer token correctly, validate environment (sandbox vs prod), inspect recent permission changes and audit logs."
  },
  "retrieved_kb_articles": [
    {
      "title": "API Authentication Error",
      "content": "For API authentication errors..."
    }
  ],
  "escalation_required": false,
  "human_handoff_context": null,
  "response": "Thanks for the detail. Based on our KB: ...",
  "llm_used": false
}
```

---

## 2. Frustrated User - unable to login

**Request**

```json
{
  "customer_query": "This is absurd - I've tried five times and login is STILL NOT WORKING. I'm really frustrated."
}
```

**Response highlights**

- `detected_persona`: `Frustrated User`
- `retrieved_kb.title`: `Login Issue`
- `escalation_required`: `true`
- `human_handoff_context`: populated with persona, summary, KB title, reason, recommended action
- `llm_used`: `false`

---

## 3. Business Executive - SLA and downtime (`POST /chat`)

**Request**

```http
POST /chat HTTP/1.1
Content-Type: application/json

{
  "messages": [
    {
      "role": "user",
      "content": "We have an enterprise SLA - this downtime is causing client impact and worrying contract risk."
    }
  ]
}
```

**Response shape**

```json
{
  "message": {
    "role": "assistant",
    "content": "Executive summary: we've matched your report..."
  },
  "detected_persona": "Business Executive",
  "retrieved_kb": { "title": "Service Downtime", "content": "..." },
  "retrieved_kb_articles": [{ "title": "Service Downtime", "content": "..." }],
  "escalation_required": true,
  "human_handoff_context": { "...": "..." },
  "llm_used": false
}
```

---

## 4. Multi-turn - follow-up inherits earlier keywords

The server scores KB articles using a **short window of recent user turns** (last two user messages blended) so terse follow-ups stay on topic.

**Request**

```json
{
  "messages": [
    { "role": "user", "content": "VPN blocks your dashboard websocket" },
    { "role": "assistant", "content": "Here is what Networking Requirements usually cover..." },
    { "role": "user", "content": "What IP allowlist applies?" }
  ]
}
```

Expect `retrieved_kb_articles` to include **`VPN, Firewall and Network Access`** along with potentially other overlapping articles when keywords tie.
