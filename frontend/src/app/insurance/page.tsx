"use client";

import { FormEvent, useState } from "react";
import { useSelector } from "react-redux";
import { api } from "@/lib/api";
import { RootState } from "@/store";

export default function InsurancePage() {
  const token = useSelector((s: RootState) => s.auth.accessToken);
  const [form, setForm] = useState({
    policy_number: "HP-99881",
    provider_name: "HealthPlus",
    procedure: "MRI",
    hospital_name: "City General Hospital",
  });
  const [result, setResult] = useState<any>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    setResult(await api.insurance(token, form));
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <form onSubmit={onSubmit} className="glass rounded-3xl p-6 shadow-soft">
        <h1 className="font-display text-3xl font-semibold">Insurance Validation</h1>
        <div className="mt-4 space-y-3">
          {Object.entries(form).map(([key, value]) => (
            <input
              key={key}
              className="w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2 dark:bg-black/20"
              value={value}
              placeholder={key}
              onChange={(e) => setForm({ ...form, [key]: e.target.value })}
            />
          ))}
        </div>
        <button className="mt-4 rounded-full bg-sea px-5 py-2.5 font-semibold text-white">Validate</button>
      </form>
      <div className="glass rounded-3xl p-6 shadow-soft text-sm">
        <h2 className="font-display text-xl font-semibold">Coverage estimate</h2>
        {result ? (
          <div className="mt-4 space-y-2">
            <p>Valid: {String(result.is_valid)}</p>
            <p>Claim eligible: {String(result.claim_eligible)}</p>
            <p>Network: {result.network_status}</p>
            <p>{result.coverage_summary}</p>
          </div>
        ) : (
          <p className="mt-3 opacity-70">Preliminary eligibility only — insurer decides final coverage.</p>
        )}
      </div>
    </div>
  );
}
