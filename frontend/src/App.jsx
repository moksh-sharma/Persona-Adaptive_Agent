import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function parseApiError(res, data) {
  let errMsg =
    typeof data?.detail === "string" ? data.detail : `Request failed (${res.status})`;
  if (Array.isArray(data?.detail)) {
    errMsg = data.detail
      .map((d) => (typeof d.msg === "string" ? d.msg : JSON.stringify(d)))
      .join("; ");
  }
  return errMsg;
}

/** Bottom-right Ollama-only chat about the demo project (POST /tool-chat, no KB). */
function FloatingToolChat() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const scrollRef = useRef(null);

  const canSend = useMemo(() => draft.trim().length > 0 && !loading, [draft, loading]);

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, loading, open]);

  useEffect(() => {
    if (!open) return;
    function onKey(e) {
      if (e.key === "Escape") setOpen(false);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  async function onSend(e) {
    e.preventDefault();
    if (!canSend) return;
    const text = draft.trim();
    const prior = messages;
    const history = [...prior, { role: "user", content: text }];
    setMessages(history);
    setDraft("");
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/tool-chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: history }),
      });
      const data = await res.json().catch(() => null);
      if (!res.ok) throw new Error(parseApiError(res, data));
      const assistantText = data?.message?.content ?? "";
      if (!assistantText) throw new Error("Empty response from tool assistant.");
      setMessages([...history, { role: "assistant", content: assistantText }]);
    } catch (err) {
      setError(err.message || "Something went wrong");
      setMessages(prior);
      setDraft(text);
    } finally {
      setLoading(false);
    }
  }

  function clearThread() {
    setMessages([]);
    setError(null);
  }

  const closePanel = useCallback(() => setOpen(false), []);

  return (
    <div className="float-chat-root">
      {open && (
        <>
          <button
            type="button"
            className="float-chat-backdrop"
            aria-hidden="true"
            tabIndex={-1}
            onClick={closePanel}
          />
          <div
            id="tool-guide-dialog"
            className="float-chat-panel card"
            role="dialog"
            aria-modal="true"
            aria-labelledby="tool-guide-title"
          >
            <div className="float-chat-header">
              <strong id="tool-guide-title">Tool Guide</strong>
              <div className="float-chat-header-actions">
                <button type="button" className="btn ghost small" onClick={clearThread}>
                  Clear
                </button>
                <button type="button" className="btn ghost small" onClick={closePanel}>
                  Close
                </button>
              </div>
            </div>
            <div className="float-chat-messages" ref={scrollRef} aria-live="polite">
              {messages.length === 0 && !loading && (
                <p className="float-chat-empty">
                  Ask about running the stack, env vars, or API routes. Requires Ollama when enabled.
                </p>
              )}
              {messages.map((m, i) => (
                <div key={i} className={`float-msg ${m.role}`}>
                  {m.content}
                </div>
              ))}
              {loading && (
                <div className="float-msg assistant muted" aria-busy="true">
                  <span className="typing-dots" aria-hidden="true">
                    <span />
                    <span />
                    <span />
                  </span>{" "}
                  Thinking
                </div>
              )}
            </div>
            {error && (
              <div className="banner error tight" role="alert">
                {error}
              </div>
            )}
            <form className="float-chat-form" onSubmit={onSend}>
              <label className="sr-only" htmlFor="tool-chat-input">
                Message to tool guide
              </label>
              <textarea
                id="tool-chat-input"
                className="textarea compact"
                placeholder="How do I enable Ollama for this project?"
                rows={2}
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                disabled={loading}
              />
              <button className="btn primary full" type="submit" disabled={!canSend}>
                {loading ? "Sending…" : "Send"}
              </button>
            </form>
          </div>
        </>
      )}
      <button
        type="button"
        className="float-chat-fab"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-controls={open ? "tool-guide-dialog" : undefined}
        aria-label={open ? "Close tool guide" : "Open tool guide (Ollama, project help)"}
      >
        {open ? "×" : "?"}
      </button>
    </div>
  );
}

export default function App() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const canSubmit = useMemo(() => query.trim().length > 0 && !loading, [query, loading]);

  async function onSubmit(e) {
    e.preventDefault();
    if (!canSubmit) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`${API_BASE}/support`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ customer_query: query.trim() }),
      });
      const data = await res.json().catch(() => null);
      if (!res.ok) throw new Error(parseApiError(res, data));
      setResult(data);
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <header className="hero">
        <h1>Persona-Adaptive Customer Support Agent</h1>
        <p className="lede">
          Describe a customer message. Persona routing uses keywords; answers blend{" "}
          <strong>knowledge-base excerpts</strong> with <strong>optional Ollama</strong> (
          <code className="inline">LLM_PROVIDER=ollama</code>). If the model is off, replies fall back to rules. Use the{" "}
          <strong className="nowrap">? button</strong> in the corner for <strong>Ollama-only project help</strong> (no
          support KB).
        </p>
      </header>

      <main className="surface">
        <form className="composer" onSubmit={onSubmit} aria-busy={loading}>
          <label className="label" htmlFor="q">
            Customer query
          </label>
          <textarea
            id="q"
            className="textarea"
            placeholder="Example: We're seeing 401s on `/v1/oauth/token` - can you check token scopes?"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            rows={5}
            disabled={loading}
            autoComplete="off"
          />
          <div className="actions">
            <button className={`btn primary${loading ? " btn-loading" : ""}`} type="submit" disabled={!canSubmit}>
              {!loading ? "Analyze & reply" : "Processing…"}
            </button>
          </div>
        </form>

        {error && (
          <div className="banner error" role="alert">
            {error}
          </div>
        )}

        {result && (
          <section className="results vault" aria-label="Pipeline output">
            <div className="results-divider">
              <span>Output</span>
            </div>
            <div className="grid">
              <div className="tile">
                <h3 className="tile-label">Detected persona</h3>
                <p className="value">{result.detected_persona}</p>
              </div>
              <div className="tile">
                <h3 className="tile-label">Primary KB</h3>
                <p className="value">{result.retrieved_kb?.title}</p>
              </div>
              <div className="tile">
                <h3 className="tile-label">Escalation</h3>
                <p className="value">{result.escalation_required ? "Required" : "Not required"}</p>
                {result.escalation_required && <span className="chip chip-warn">Handoff flagged</span>}
              </div>
            </div>
            {(result.retrieved_kb_articles?.length ?? 0) > 1 && (
              <div className="panel subtle">
                <h3 className="panel-heading">Articles combined for context</h3>
                <ul className="kb-inline-list">
                  {result.retrieved_kb_articles.map((a) => (
                    <li key={a.title}>{a.title}</li>
                  ))}
                </ul>
              </div>
            )}
            <div className="panel subtle">
              <h3 className="panel-heading">Knowledge base excerpt</h3>
              <p className="body-text muted">{result.retrieved_kb?.content}</p>
            </div>
            {result.escalation_required && result.human_handoff_context && (
              <div className="panel warn">
                <h3 className="panel-heading">Human handoff context</h3>
                <pre className="json">{JSON.stringify(result.human_handoff_context, null, 2)}</pre>
              </div>
            )}
            <div className={`panel highlight${result.llm_used ? " highlight-llm" : ""}`}>
              <div className="panel-head">
                <h3 className="panel-heading mb-0">Agent response</h3>
                <span className={`chip ${result.llm_used ? "chip-llm" : "chip-rules"}`}>
                  {result.llm_used ? "Ollama" : "Rules"}
                </span>
              </div>
              <p className="body-text response-body">{result.response}</p>
            </div>
          </section>
        )}
      </main>

      <FloatingToolChat />
    </div>
  );
}
