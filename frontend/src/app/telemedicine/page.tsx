"use client";

import { FormEvent, useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { api } from "@/lib/api";
import { RootState } from "@/store";

export default function TelemedicinePage() {
  const token = useSelector((s: RootState) => s.auth.accessToken);
  const [doctors, setDoctors] = useState<any[]>([]);
  const [doctorId, setDoctorId] = useState("");
  const [reason, setReason] = useState("Virtual consultation");
  const [session, setSession] = useState<any>(null);
  const [sessions, setSessions] = useState<any[]>([]);

  useEffect(() => {
    if (!token) return;
    api.doctors(token).then((d) => {
      setDoctors(d);
      if (d[0]) setDoctorId(String(d[0].id));
    });
    api.telemedicineSessions(token).then(setSessions).catch(() => undefined);
  }, [token]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    const res = await api.startTelemedicine(token, {
      doctor_id: Number(doctorId),
      reason,
    });
    setSession(res);
    setSessions(await api.telemedicineSessions(token));
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <form onSubmit={onSubmit} className="glass rounded-3xl p-6 shadow-soft">
        <h1 className="font-display text-3xl font-semibold">Telemedicine</h1>
        <p className="mt-2 text-sm opacity-70">Create a virtual visit room with a clinician.</p>
        <select
          className="mt-4 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2 dark:bg-black/20"
          value={doctorId}
          onChange={(e) => setDoctorId(e.target.value)}
        >
          {doctors.map((d) => (
            <option key={d.id} value={d.id}>
              {d.full_name} — {d.specialty}
            </option>
          ))}
        </select>
        <input
          className="mt-3 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2 dark:bg-black/20"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
        />
        <button className="mt-4 rounded-full bg-sea px-5 py-2.5 font-semibold text-white">Start session</button>
        {session && (
          <div className="mt-4 rounded-2xl bg-white/50 p-4 text-sm dark:bg-white/5">
            <p><strong>Session:</strong> {session.session_id}</p>
            <p><strong>Room:</strong> {session.room_url}</p>
            <ul className="mt-2 list-disc pl-5">
              {session.instructions?.map((i: string, idx: number) => <li key={idx}>{i}</li>)}
            </ul>
          </div>
        )}
      </form>
      <div className="glass rounded-3xl p-6 shadow-soft">
        <h2 className="font-display text-xl font-semibold">Recent sessions</h2>
        <ul className="mt-4 space-y-2 text-sm">
          {sessions.map((s) => (
            <li key={s.session_id} className="rounded-2xl bg-white/50 p-3 dark:bg-white/5">
              {s.session_id} · Doctor {s.doctor_id} · {s.status}
            </li>
          ))}
          {sessions.length === 0 && <li className="opacity-70">No sessions yet.</li>}
        </ul>
      </div>
    </div>
  );
}
