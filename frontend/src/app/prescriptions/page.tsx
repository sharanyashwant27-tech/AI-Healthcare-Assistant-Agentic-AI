"use client";

import { FormEvent, useState } from "react";
import { useSelector } from "react-redux";
import { api } from "@/lib/api";
import { RootState } from "@/store";

export default function PrescriptionsPage() {
  const token = useSelector((s: RootState) => s.auth.accessToken);
  const [text, setText] = useState("Paracetamol 500mg twice daily for 3 days\nIbuprofen 400mg as needed");
  const [allergies, setAllergies] = useState("Penicillin");
  const [result, setResult] = useState<any>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    setResult(await api.prescriptionText(token, text, allergies));
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <form onSubmit={onSubmit} className="glass rounded-3xl p-6 shadow-soft">
        <h1 className="font-display text-3xl font-semibold">Prescription Analysis</h1>
        <textarea
          className="mt-4 min-h-40 w-full rounded-2xl border border-[var(--line)] bg-white/70 p-3 dark:bg-black/20"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <input
          className="mt-3 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2 dark:bg-black/20"
          value={allergies}
          onChange={(e) => setAllergies(e.target.value)}
          placeholder="Known allergies"
        />
        <button className="mt-4 rounded-full bg-sea px-5 py-2.5 font-semibold text-white">Analyze</button>
      </form>
      <div className="glass rounded-3xl p-6 shadow-soft text-sm">
        <h2 className="font-display text-xl font-semibold">Extracted insights</h2>
        {result ? (
          <pre className="mt-4 overflow-auto whitespace-pre-wrap rounded-2xl bg-white/50 p-4 dark:bg-white/5">
            {JSON.stringify(result, null, 2)}
          </pre>
        ) : (
          <p className="mt-3 opacity-70">Paste prescription text or OCR output.</p>
        )}
      </div>
    </div>
  );
}
