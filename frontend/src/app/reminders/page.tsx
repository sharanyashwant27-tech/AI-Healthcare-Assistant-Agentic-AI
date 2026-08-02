"use client";

import { FormEvent, useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { api } from "@/lib/api";
import { RootState } from "@/store";

export default function RemindersPage() {
  const token = useSelector((s: RootState) => s.auth.accessToken);
  const [medicine, setMedicine] = useState("Paracetamol");
  const [dosage, setDosage] = useState("500mg");
  const [schedule, setSchedule] = useState("08:00,20:00");
  const [items, setItems] = useState<any[]>([]);

  async function refresh() {
    if (!token) return;
    setItems(await api.reminders(token));
  }

  useEffect(() => {
    refresh().catch(() => undefined);
  }, [token]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    await api.createReminder(token, {
      medicine_name: medicine,
      dosage,
      schedule,
    });
    await refresh();
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <form onSubmit={onSubmit} className="glass rounded-3xl p-6 shadow-soft">
        <h1 className="font-display text-3xl font-semibold">Medication Reminder</h1>
        <input className="mt-4 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2 dark:bg-black/20" value={medicine} onChange={(e) => setMedicine(e.target.value)} placeholder="Medicine" />
        <input className="mt-3 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2 dark:bg-black/20" value={dosage} onChange={(e) => setDosage(e.target.value)} placeholder="Dosage" />
        <input className="mt-3 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2 dark:bg-black/20" value={schedule} onChange={(e) => setSchedule(e.target.value)} placeholder="Schedule HH:MM,HH:MM" />
        <button className="mt-4 rounded-full bg-sea px-5 py-2.5 font-semibold text-white">Save reminder</button>
      </form>
      <div className="glass rounded-3xl p-6 shadow-soft">
        <h2 className="font-display text-xl font-semibold">Active reminders</h2>
        <ul className="mt-4 space-y-2 text-sm">
          {items.map((i) => (
            <li key={i.id} className="rounded-2xl bg-white/50 p-3 dark:bg-white/5">
              <p className="font-medium">{i.title}</p>
              <p className="opacity-70">{i.message}</p>
            </li>
          ))}
          {items.length === 0 && <li className="opacity-70">No reminders yet.</li>}
        </ul>
      </div>
    </div>
  );
}
