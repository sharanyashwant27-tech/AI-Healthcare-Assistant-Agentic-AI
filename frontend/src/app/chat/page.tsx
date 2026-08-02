"use client";

import { FormEvent, useState } from "react";
import { useSelector } from "react-redux";
import { api } from "@/lib/api";
import { RootState } from "@/store";

type Msg = {
  role: "user" | "assistant";
  content: string;
  meta?: string;
  citations?: any[];
  confidence?: any;
  explanation?: any;
  human_review?: any;
};

export default function ChatPage() {
  const token = useSelector((s: RootState) => s.auth.accessToken);
  const [messages, setMessages] = useState<Msg[]>([
    {
      role: "assistant",
      content:
        "Hello. I use hybrid RAG + GraphRAG with multi-agent collaboration. I do not diagnose with certainty.",
    },
  ]);
  const [input, setInput] = useState("");
  const [language, setLanguage] = useState("en");
  const [conversationId, setConversationId] = useState<string>();
  const [loading, setLoading] = useState(false);
  const [lastEvidence, setLastEvidence] = useState<Msg | null>(null);

  async function send(e: FormEvent) {
    e.preventDefault();
    if (!token || !input.trim()) return;
    const text = input.trim();
    setInput("");
    setMessages((m) => [...m, { role: "user", content: text }]);
    setLoading(true);
    try {
      const res = await api.chat(token, text, conversationId, { language, enable_hitl: true });
      setConversationId(res.conversation_id);
      const assistant: Msg = {
        role: "assistant",
        content: res.reply,
        meta: [
          res.agent,
          res.risk_level ? `risk ${res.risk_level}` : null,
          res.confidence?.label ? `confidence ${res.confidence.label}` : null,
          res.human_review?.required ? "HITL pending" : null,
        ]
          .filter(Boolean)
          .join(" · "),
        citations: res.citations,
        confidence: res.confidence,
        explanation: res.explanation,
        human_review: res.human_review,
      };
      setMessages((m) => [...m, assistant]);
      setLastEvidence(assistant);
    } catch (err: any) {
      setMessages((m) => [...m, { role: "assistant", content: err.message }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-4 lg:grid-cols-[1.4fr_0.6fr]">
      <div className="glass flex min-h-[70vh] flex-col rounded-3xl p-5 shadow-soft">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <h1 className="font-display text-3xl font-semibold">AI Chat</h1>
          <label className="text-sm opacity-70">
            Language{" "}
            <select
              className="ml-2 rounded-full border border-[var(--line)] bg-white/70 px-3 py-1 dark:bg-black/20"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              <option value="en">English</option>
              <option value="hi">Hindi</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="ar">Arabic</option>
              <option value="zh">Chinese</option>
            </select>
          </label>
        </div>
        <div className="mt-4 flex-1 space-y-3 overflow-y-auto">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                m.role === "user"
                  ? "ml-auto bg-sea text-white"
                  : "bg-white/70 dark:bg-white/5"
              }`}
            >
              <p className="whitespace-pre-wrap text-sm">{m.content}</p>
              {m.meta && <p className="mt-1 text-xs opacity-60">{m.meta}</p>}
            </div>
          ))}
        </div>
        <form onSubmit={send} className="mt-4 flex gap-2">
          <input
            className="flex-1 rounded-full border border-[var(--line)] bg-white/70 px-4 py-3 dark:bg-black/20"
            placeholder="Ask about symptoms, guidelines, appointments…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button disabled={loading} className="rounded-full bg-sea px-5 py-3 font-semibold text-white">
            {loading ? "…" : "Send"}
          </button>
        </form>
      </div>
      <aside className="glass h-fit space-y-4 rounded-3xl p-5 text-sm shadow-soft">
        <div>
          <h2 className="font-display text-xl font-semibold">Explainable evidence</h2>
          <p className="mt-2 opacity-70">
            {lastEvidence?.explanation?.method || "Citations and graph paths appear after an answer."}
          </p>
          {lastEvidence?.confidence && (
            <p className="mt-2">
              Confidence: <strong>{lastEvidence.confidence.label}</strong> (
              {lastEvidence.confidence.score})
            </p>
          )}
          <ul className="mt-3 space-y-2">
            {(lastEvidence?.citations || []).map((c: any) => (
              <li key={c.id} className="rounded-2xl bg-white/50 p-3 dark:bg-white/5">
                <p className="font-medium">
                  [{c.id}] {c.source_name}
                </p>
                <p className="opacity-70">{c.quote}</p>
              </li>
            ))}
          </ul>
          {lastEvidence?.human_review?.required && (
            <p className="mt-3 rounded-2xl border border-coral/40 bg-coral/10 p-3 text-coral">
              Human-in-the-loop review queued ({lastEvidence.human_review.review_id || "pending"}).
            </p>
          )}
        </div>
        <div>
          <h2 className="font-display text-xl font-semibold">Safety</h2>
          <p className="mt-2 opacity-70">
            Not a diagnosis. High-risk drafts require clinician review. Memory is used longitudinally in this
            conversation.
          </p>
        </div>
      </aside>
    </div>
  );
}
