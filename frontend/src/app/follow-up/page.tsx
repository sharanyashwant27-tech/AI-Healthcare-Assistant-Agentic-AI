"use client";

import { FormEvent, useState } from "react";
import { useSelector } from "react-redux";
import { AppLink } from "@/components/AppLink";
import { api } from "@/lib/api";
import { RootState } from "@/store";

export default function FollowUpPage() {
  const token = useSelector((s: RootState) => s.auth.accessToken);
  const [reason, setReason] = useState("Post-illness clinical review");
  const [days, setDays] = useState(7);
  const [tests, setTests] = useState("CBC, Blood sugar");
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    setLoading(true);
    setError("");
    try {
      setResult(
        await api.followUp(token, {
          reason,
          days,
          tests: tests.split(",").map((t) => t.trim()).filter(Boolean),
        })
      );
    } catch (err: any) {
      setError(err.message || "Follow-up failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <form onSubmit={onSubmit} className="glass rounded-3xl p-6 shadow-soft">
        <h1 className="font-display text-3xl font-semibold">Follow-up Agent</h1>
        <p className="mt-2 text-sm opacity-70">Schedule follow-ups, tests, and reminders.</p>
        <input
          className="mt-4 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2 dark:bg-black/20"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
        />
        <input
          type="number"
          className="mt-3 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2 dark:bg-black/20"
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
        />
        <input
          className="mt-3 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2 dark:bg-black/20"
          value={tests}
          onChange={(e) => setTests(e.target.value)}
          placeholder="Recommended tests (comma separated)"
        />
        {error && <p className="mt-3 text-sm text-coral">{error}</p>}
        <button
          disabled={loading}
          className="mt-4 rounded-full bg-sea px-5 py-2.5 font-semibold text-white disabled:opacity-60"
        >
          {loading ? "Creating…" : "Create plan"}
        </button>
        <div className="mt-4 flex flex-wrap gap-3 text-sm">
          <AppLink href="/appointments" className="text-sea underline">
            Appointments
          </AppLink>
          <AppLink href="/reminders" className="text-sea underline">
            Reminders
          </AppLink>
          <AppLink href="/labs" className="text-sea underline">
            Labs
          </AppLink>
        </div>
      </form>
      <div className="glass rounded-3xl p-6 shadow-soft text-sm">
        <h2 className="font-display text-xl font-semibold">Plan</h2>
        {result ? (
          <pre className="mt-4 overflow-auto whitespace-pre-wrap rounded-2xl bg-white/50 p-4 dark:bg-white/5">
            {JSON.stringify(result, null, 2)}
          </pre>
        ) : (
          <p className="mt-3 opacity-70">Submit to generate a follow-up schedule.</p>
        )}
      </div>
    </div>
  );
}
