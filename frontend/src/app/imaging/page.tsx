"use client";

import { FormEvent, useState } from "react";
import { useSelector } from "react-redux";
import { api } from "@/lib/api";
import { RootState } from "@/store";

export default function ImagingPage() {
  const token = useSelector((s: RootState) => s.auth.accessToken);
  const [file, setFile] = useState<File | null>(null);
  const [modality, setModality] = useState("xray");
  const [notes, setNotes] = useState("");
  const [result, setResult] = useState<any>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    setResult(await api.medicalImage(token, file, modality, notes));
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <form onSubmit={onSubmit} className="glass rounded-3xl p-6 shadow-soft">
        <h1 className="font-display text-3xl font-semibold">Medical Image Assistant</h1>
        <p className="mt-2 text-sm opacity-70">Assistive only — not a radiology report.</p>
        <select
          className="mt-4 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2 dark:bg-black/20"
          value={modality}
          onChange={(e) => setModality(e.target.value)}
        >
          <option value="xray">X-Ray</option>
          <option value="ct">CT</option>
          <option value="mri">MRI</option>
          <option value="ultrasound">Ultrasound</option>
        </select>
        <input
          type="file"
          accept="image/*,.pdf"
          className="mt-3 w-full text-sm"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
        <textarea
          className="mt-3 min-h-28 w-full rounded-2xl border border-[var(--line)] bg-white/70 p-3 dark:bg-black/20"
          placeholder="Clinical notes / indication"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
        <button className="mt-4 rounded-full bg-sea px-5 py-2.5 font-semibold text-white">Analyze</button>
      </form>
      <div className="glass rounded-3xl p-6 shadow-soft text-sm">
        <h2 className="font-display text-xl font-semibold">Findings</h2>
        {result ? (
          <div className="mt-4 space-y-2">
            <p><strong>Modality:</strong> {result.modality}</p>
            <ul className="list-disc pl-5">
              {result.findings?.map((f: string, i: number) => <li key={i}>{f}</li>)}
            </ul>
            <p>{result.summary}</p>
            <p className="text-xs opacity-60">{result.uncertainty_note}</p>
          </div>
        ) : (
          <p className="mt-3 opacity-70">Upload an image or report overlay for assistive review.</p>
        )}
      </div>
    </div>
  );
}
