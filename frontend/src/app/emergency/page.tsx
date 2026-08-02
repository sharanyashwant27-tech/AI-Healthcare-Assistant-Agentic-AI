"use client";

import { FormEvent, useState } from "react";
import { useSelector } from "react-redux";
import { api } from "@/lib/api";
import { RootState } from "@/store";

export default function EmergencyPage() {
  const token = useSelector((s: RootState) => s.auth.accessToken);
  const [symptoms, setSymptoms] = useState("chest pain, sweating");
  const [description, setDescription] = useState("");
  const [result, setResult] = useState<any>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    setResult(
      await api.emergency(token, {
        symptoms: symptoms.split(",").map((s) => s.trim()),
        description,
      })
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <form onSubmit={onSubmit} className="glass rounded-3xl p-6 shadow-soft">
        <h1 className="font-display text-3xl font-semibold text-coral">Emergency Check</h1>
        <p className="mt-2 text-sm opacity-70">
          If you think you are having an emergency, call local emergency services now.
        </p>
        <input
          className="mt-4 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2 dark:bg-black/20"
          value={symptoms}
          onChange={(e) => setSymptoms(e.target.value)}
        />
        <textarea
          className="mt-3 min-h-28 w-full rounded-2xl border border-[var(--line)] bg-white/70 p-3 dark:bg-black/20"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Additional description"
        />
        <button className="mt-4 rounded-full bg-coral px-5 py-2.5 font-semibold text-white">Assess</button>
      </form>
      <div className="glass rounded-3xl p-6 shadow-soft text-sm">
        <h2 className="font-display text-xl font-semibold">Assessment</h2>
        {result ? (
          <div className="mt-4 space-y-2">
            <p className={result.is_emergency ? "font-semibold text-coral" : ""}>
              Emergency: {String(result.is_emergency)} {result.emergency_type || ""}
            </p>
            <ul className="list-disc pl-5">
              {result.immediate_actions?.map((a: string, i: number) => (
                <li key={i}>{a}</li>
              ))}
            </ul>
            <p>{result.message}</p>
          </div>
        ) : (
          <p className="mt-3 opacity-70">Red-flag screening for heart attack, stroke, fever, and breathing issues.</p>
        )}
      </div>
    </div>
  );
}
