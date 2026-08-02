"use client";

import { FormEvent, useState } from "react";
import { useSelector } from "react-redux";
import { api } from "@/lib/api";
import { RootState } from "@/store";

export default function LabsPage() {
  const token = useSelector((s: RootState) => s.auth.accessToken);
  const [text, setText] = useState(
    "CBC Report\nHemoglobin: 11.2\nWBC: 12000\nPlatelets: 180000\nGlucose: 128\nCreatinine: 1.1\nALT: 62\nAST: 48"
  );
  const [result, setResult] = useState<any>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    setResult(await api.labText(token, text));
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <form onSubmit={onSubmit} className="glass rounded-3xl p-6 shadow-soft">
        <h1 className="font-display text-3xl font-semibold">Lab Report Analysis</h1>
        <textarea
          className="mt-4 min-h-48 w-full rounded-2xl border border-[var(--line)] bg-white/70 p-3 dark:bg-black/20"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <button className="mt-4 rounded-full bg-sea px-5 py-2.5 font-semibold text-white">Summarize</button>
      </form>
      <div className="glass rounded-3xl p-6 shadow-soft text-sm">
        <h2 className="font-display text-xl font-semibold">Summary</h2>
        {result ? (
          <div className="mt-4 space-y-2">
            <p><strong>Type:</strong> {result.report_type}</p>
            <p><strong>Abnormalities:</strong> {(result.abnormalities || []).join("; ") || "None flagged"}</p>
            <p>{result.summary}</p>
          </div>
        ) : (
          <p className="mt-3 opacity-70">Upload/paste CBC, liver, kidney, or glucose panels.</p>
        )}
      </div>
    </div>
  );
}
