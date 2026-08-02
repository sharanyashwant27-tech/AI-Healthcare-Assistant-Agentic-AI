"use client";

import { FormEvent, useState } from "react";
import { useSelector } from "react-redux";
import { api } from "@/lib/api";
import { RootState } from "@/store";

export default function SymptomsPage() {
  const token = useSelector((s: RootState) => s.auth.accessToken);
  const [symptoms, setSymptoms] = useState("fever, cough");
  const [age, setAge] = useState("32");
  const [gender, setGender] = useState("female");
  const [history, setHistory] = useState("");
  const [medicines, setMedicines] = useState("");
  const [allergies, setAllergies] = useState("");
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    setError("");
    try {
      const res = await api.symptomAnalysis(token, {
        symptoms: symptoms.split(",").map((s) => s.trim()).filter(Boolean),
        severity: "moderate",
        age: age ? Number(age) : undefined,
        gender: gender || undefined,
        medical_history: history || undefined,
        current_medicines: medicines || undefined,
        allergies: allergies || undefined,
        patient_type: "patient",
        country: "IN",
      });
      setResult(res);
    } catch (err: any) {
      setError(err.message);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <form onSubmit={onSubmit} className="glass rounded-3xl p-6 shadow-soft">
        <h1 className="font-display text-3xl font-semibold">Symptom Analysis</h1>
        <p className="mt-2 text-sm opacity-70">
          Possible conditions, risk, specialist, urgency — never a certain diagnosis.
        </p>
        <label className="mt-4 block text-sm opacity-70">Symptoms</label>
        <textarea
          className="mt-1 min-h-24 w-full rounded-2xl border border-[var(--line)] bg-white/70 p-3 dark:bg-black/20"
          value={symptoms}
          onChange={(e) => setSymptoms(e.target.value)}
        />
        <div className="mt-3 grid grid-cols-2 gap-3">
          <div>
            <label className="text-sm opacity-70">Age</label>
            <input
              className="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white/70 p-3 dark:bg-black/20"
              value={age}
              onChange={(e) => setAge(e.target.value)}
            />
          </div>
          <div>
            <label className="text-sm opacity-70">Gender</label>
            <input
              className="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white/70 p-3 dark:bg-black/20"
              value={gender}
              onChange={(e) => setGender(e.target.value)}
            />
          </div>
        </div>
        <label className="mt-3 block text-sm opacity-70">Medical History</label>
        <input
          className="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white/70 p-3 dark:bg-black/20"
          value={history}
          onChange={(e) => setHistory(e.target.value)}
        />
        <label className="mt-3 block text-sm opacity-70">Current Medicines</label>
        <input
          className="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white/70 p-3 dark:bg-black/20"
          value={medicines}
          onChange={(e) => setMedicines(e.target.value)}
        />
        <label className="mt-3 block text-sm opacity-70">Allergies</label>
        <input
          className="mt-1 w-full rounded-2xl border border-[var(--line)] bg-white/70 p-3 dark:bg-black/20"
          value={allergies}
          onChange={(e) => setAllergies(e.target.value)}
        />
        <button className="mt-4 rounded-full bg-sea px-5 py-2.5 font-semibold text-white">Analyze</button>
        {error && <p className="mt-3 text-coral">{error}</p>}
      </form>
      <div className="glass rounded-3xl p-6 shadow-soft">
        <h2 className="font-display text-xl font-semibold">Results</h2>
        {!result && <p className="mt-3 text-sm opacity-70">Submit symptoms to see agent output.</p>}
        {result && (
          <div className="mt-4 space-y-3 text-sm">
            <p><strong>Risk:</strong> {result.risk_level} ({result.risk_score}/100)</p>
            <p><strong>Next action:</strong> {result.next_action}</p>
            <p><strong>Urgency:</strong> {result.urgency}</p>
            <p><strong>Specialist:</strong> {result.recommended_specialist}</p>
            <p>{result.advice}</p>
            <ul className="list-disc pl-5">
              {result.possible_conditions?.map((c: any, i: number) => (
                <li key={i}>{c.condition} ({c.likelihood})</li>
              ))}
            </ul>
            <p className="text-xs opacity-60">{result.disclaimer}</p>
          </div>
        )}
      </div>
    </div>
  );
}
