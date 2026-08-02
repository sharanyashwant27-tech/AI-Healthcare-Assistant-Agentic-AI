"use client";

import { FormEvent, useState } from "react";
import { useSelector } from "react-redux";
import { api } from "@/lib/api";
import { RootState } from "@/store";

export default function KnowledgePage() {
  const token = useSelector((s: RootState) => s.auth.accessToken);
  const [query, setQuery] = useState("What does CDC say about chest pain emergencies?");
  const [result, setResult] = useState<any>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    setResult(await api.knowledge(token, query, true));
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <form onSubmit={onSubmit} className="glass rounded-3xl p-6 shadow-soft">
        <h1 className="font-display text-3xl font-semibold">Medical Knowledge Assistant</h1>
        <p className="mt-2 text-sm opacity-70">
          RAG: Documents → Loader → Chunking → Embeddings → Vector DB → Retriever → LLM → Answer
        </p>
        <p className="mt-2 text-xs opacity-60">
          Sources: WHO, CDC, Hospital SOP, Drug Database, Medical Books, Research Papers, Hospital Policies
        </p>
        <textarea
          className="mt-4 min-h-36 w-full rounded-2xl border border-[var(--line)] bg-white/70 p-3 dark:bg-black/20"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button className="mt-4 rounded-full bg-sea px-5 py-2.5 font-semibold text-white">Ask</button>
      </form>
      <div className="glass rounded-3xl p-6 shadow-soft text-sm">
        <h2 className="font-display text-xl font-semibold">Answer</h2>
        {result ? (
          <div className="mt-4 space-y-3">
            <p className="whitespace-pre-wrap">{result.answer}</p>
            <p className="text-xs opacity-60">{result.disclaimer}</p>
          </div>
        ) : (
          <p className="mt-3 opacity-70">Ask a guideline or disease-knowledge question.</p>
        )}
      </div>
    </div>
  );
}
