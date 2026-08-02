"use client";

import { FormEvent, useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { api } from "@/lib/api";
import { RootState } from "@/store";

export default function AppointmentsPage() {
  const token = useSelector((s: RootState) => s.auth.accessToken);
  const [doctors, setDoctors] = useState<any[]>([]);
  const [appointments, setAppointments] = useState<any[]>([]);
  const [doctorId, setDoctorId] = useState("");
  const [scheduledAt, setScheduledAt] = useState("");
  const [reason, setReason] = useState("General consultation");
  const [message, setMessage] = useState("");

  async function refresh() {
    if (!token) return;
    const [d, a] = await Promise.all([api.doctors(token), api.appointments(token)]);
    setDoctors(d);
    setAppointments(a);
    if (d[0]) setDoctorId(String(d[0].id));
  }

  useEffect(() => {
    refresh().catch((e) => setMessage(e.message));
  }, [token]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    try {
      await api.createAppointment(token, {
        doctor_id: Number(doctorId),
        scheduled_at: new Date(scheduledAt).toISOString(),
        reason,
      });
      setMessage("Appointment booked.");
      await refresh();
    } catch (err: any) {
      setMessage(err.message);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <form onSubmit={onSubmit} className="glass rounded-3xl p-6 shadow-soft">
        <h1 className="font-display text-3xl font-semibold">Book Appointment</h1>
        <label className="mt-4 block text-sm">
          Doctor
          <select
            className="mt-1 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2 dark:bg-black/20"
            value={doctorId}
            onChange={(e) => setDoctorId(e.target.value)}
          >
            {doctors.map((d) => (
              <option key={d.id} value={d.id}>
                {d.full_name} — {d.specialty}
              </option>
            ))}
          </select>
        </label>
        <label className="mt-3 block text-sm">
          Date & time
          <input
            type="datetime-local"
            className="mt-1 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2 dark:bg-black/20"
            value={scheduledAt}
            onChange={(e) => setScheduledAt(e.target.value)}
            required
          />
        </label>
        <label className="mt-3 block text-sm">
          Reason
          <input
            className="mt-1 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2 dark:bg-black/20"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
          />
        </label>
        <button className="mt-4 rounded-full bg-sea px-5 py-2.5 font-semibold text-white">Book</button>
        {message && <p className="mt-3 text-sm">{message}</p>}
      </form>
      <div className="glass rounded-3xl p-6 shadow-soft">
        <h2 className="font-display text-xl font-semibold">Your appointments</h2>
        <ul className="mt-4 space-y-3">
          {appointments.map((a) => (
            <li key={a.id} className="rounded-2xl bg-white/50 p-3 text-sm dark:bg-white/5">
              #{a.id} · Doctor {a.doctor_id} · {new Date(a.scheduled_at).toLocaleString()} · {a.status}
            </li>
          ))}
          {appointments.length === 0 && <li className="text-sm opacity-70">No appointments yet.</li>}
        </ul>
      </div>
    </div>
  );
}
