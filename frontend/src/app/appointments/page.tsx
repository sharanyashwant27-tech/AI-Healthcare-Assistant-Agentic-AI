"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useSelector } from "react-redux";
import { api } from "@/lib/api";
import { RootState } from "@/store";

export default function AppointmentsPage() {
  const token = useSelector((s: RootState) => s.auth.accessToken);
  const [doctors, setDoctors] = useState<any[]>([]);
  const [appointments, setAppointments] = useState<any[]>([]);
  const [specialty, setSpecialty] = useState("All");
  const [doctorId, setDoctorId] = useState("");
  const [scheduledAt, setScheduledAt] = useState("");
  const [reason, setReason] = useState("General consultation");
  const [message, setMessage] = useState("");

  const specialties = useMemo(() => {
    const set = new Set<string>(doctors.map((d) => d.specialty).filter(Boolean));
    return ["All", ...Array.from(set).sort()];
  }, [doctors]);

  const filteredDoctors = useMemo(() => {
    if (specialty === "All") return doctors;
    return doctors.filter((d) => d.specialty === specialty);
  }, [doctors, specialty]);

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

  useEffect(() => {
    if (!filteredDoctors.length) {
      setDoctorId("");
      return;
    }
    if (!filteredDoctors.some((d) => String(d.id) === doctorId)) {
      setDoctorId(String(filteredDoctors[0].id));
    }
  }, [filteredDoctors, doctorId]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token || !doctorId) return;
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
    <div className="space-y-6">
      <div className="glass rounded-3xl p-6 shadow-soft">
        <h1 className="font-display text-3xl font-semibold">Specialists</h1>
        <p className="mt-2 text-sm opacity-70">
          Browse doctors by category — Cardiology, Gastroenterology, ENT, and more.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          {specialties.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => setSpecialty(s)}
              className={`rounded-full px-3 py-1.5 text-sm transition ${
                specialty === s
                  ? "bg-sea text-white"
                  : "border border-[var(--line)] bg-white/50 hover:bg-white/80 dark:bg-white/5"
              }`}
            >
              {s}
            </button>
          ))}
        </div>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {filteredDoctors.map((d) => (
            <button
              key={d.id}
              type="button"
              onClick={() => setDoctorId(String(d.id))}
              className={`rounded-3xl border p-4 text-left transition ${
                String(d.id) === doctorId
                  ? "border-sea bg-sea/10"
                  : "border-[var(--line)] bg-white/40 hover:bg-white/70 dark:bg-white/5"
              }`}
            >
              <p className="font-display text-lg font-semibold">{d.full_name}</p>
              <p className="text-sm text-sea">{d.specialty}</p>
              <p className="mt-2 text-xs opacity-70">
                {d.years_experience} yrs · ★ {d.rating} · ${d.consultation_fee}
              </p>
              <p className="mt-1 line-clamp-2 text-xs opacity-60">{d.bio}</p>
            </button>
          ))}
          {!filteredDoctors.length && (
            <p className="text-sm opacity-70">No doctors in this specialty yet.</p>
          )}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <form onSubmit={onSubmit} className="glass rounded-3xl p-6 shadow-soft">
          <h2 className="font-display text-2xl font-semibold">Book Appointment</h2>
          <label className="mt-4 block text-sm">
            Specialty
            <select
              className="mt-1 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2 dark:bg-black/20"
              value={specialty}
              onChange={(e) => setSpecialty(e.target.value)}
            >
              {specialties.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </label>
          <label className="mt-3 block text-sm">
            Doctor
            <select
              className="mt-1 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2 dark:bg-black/20"
              value={doctorId}
              onChange={(e) => setDoctorId(e.target.value)}
              required
            >
              {filteredDoctors.map((d) => (
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
            {appointments.map((a) => {
              const doc = doctors.find((d) => d.id === a.doctor_id);
              return (
                <li key={a.id} className="rounded-2xl bg-white/50 p-3 text-sm dark:bg-white/5">
                  #{a.id} · {doc ? `${doc.full_name} (${doc.specialty})` : `Doctor ${a.doctor_id}`} ·{" "}
                  {new Date(a.scheduled_at).toLocaleString()} · {a.status}
                </li>
              );
            })}
            {appointments.length === 0 && <li className="text-sm opacity-70">No appointments yet.</li>}
          </ul>
        </div>
      </div>
    </div>
  );
}
