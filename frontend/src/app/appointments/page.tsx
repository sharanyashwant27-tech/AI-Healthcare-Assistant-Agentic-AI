"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useSelector } from "react-redux";
import { api } from "@/lib/api";
import { RootState } from "@/store";

type Doctor = {
  id: number;
  full_name?: string | null;
  specialty?: string | null;
};

type Appointment = {
  id: number;
  doctor_id: number;
  scheduled_at: string;
  status: string;
  reason?: string | null;
};

export default function AppointmentsPage() {
  const token = useSelector((s: RootState) => s.auth.accessToken);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [specialty, setSpecialty] = useState("");
  const [doctorId, setDoctorId] = useState("");
  const [scheduledAt, setScheduledAt] = useState("");
  const [reason, setReason] = useState("General consultation");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [booking, setBooking] = useState(false);

  const specialties = useMemo(() => {
    const set = new Set<string>(doctors.map((d) => d.specialty).filter(Boolean) as string[]);
    return Array.from(set).sort();
  }, [doctors]);

  const filteredDoctors = useMemo(() => {
    if (!specialty) return [];
    return doctors.filter((d) => d.specialty === specialty);
  }, [doctors, specialty]);

  async function refresh() {
    if (!token) return;
    try {
      const [d, a] = await Promise.all([api.doctors(token), api.appointments(token)]);
      setDoctors(d);
      setAppointments(a);
      setError("");
    } catch (e: any) {
      setError(e.message || "Failed to load specialists");
    }
  }

  useEffect(() => {
    refresh().catch((e) => setError(e.message));
  }, [token]);

  useEffect(() => {
    if (!specialty && specialties.length) {
      setSpecialty(specialties[0]);
    }
  }, [specialties, specialty]);

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
    if (!token || !specialty || !doctorId || !scheduledAt) return;

    const when = new Date(scheduledAt);
    if (Number.isNaN(when.getTime()) || when.getTime() < Date.now()) {
      setError("Please choose a future date and time.");
      return;
    }

    setBooking(true);
    setMessage("");
    setError("");
    try {
      await api.createAppointment(token, {
        doctor_id: Number(doctorId),
        scheduled_at: when.toISOString(),
        reason: reason.trim() || "General consultation",
      });
      setMessage("Appointment booked.");
      await refresh();
    } catch (err: any) {
      setError(err.message || "Could not book appointment");
    } finally {
      setBooking(false);
    }
  }

  if (!token) {
    return (
      <div className="glass rounded-3xl p-6 shadow-soft">
        <h1 className="font-display text-3xl font-semibold">Specialists</h1>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <form onSubmit={onSubmit} className="glass rounded-3xl p-6 shadow-soft">
        <h1 className="font-display text-3xl font-semibold">Specialists</h1>

        <label className="mt-6 block text-sm font-medium">
          Category
          <select
            className="mt-1 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2.5 dark:bg-black/20"
            value={specialty}
            onChange={(e) => {
              setSpecialty(e.target.value);
              setMessage("");
              setError("");
            }}
            required
          >
            {!specialties.length && <option value="">Loading…</option>}
            {specialties.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>

        <label className="mt-4 block text-sm font-medium">
          Doctor
          <select
            className="mt-1 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2.5 dark:bg-black/20"
            value={doctorId}
            onChange={(e) => {
              setDoctorId(e.target.value);
              setMessage("");
              setError("");
            }}
            required
          >
            {!filteredDoctors.length && <option value="">No doctors</option>}
            {filteredDoctors.map((d) => (
              <option key={d.id} value={d.id}>
                {d.full_name || `Doctor #${d.id}`}
              </option>
            ))}
          </select>
        </label>

        <label className="mt-4 block text-sm font-medium">
          Date & time
          <input
            type="datetime-local"
            className="mt-1 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2.5 dark:bg-black/20"
            value={scheduledAt}
            onChange={(e) => setScheduledAt(e.target.value)}
            required
          />
        </label>

        <label className="mt-4 block text-sm font-medium">
          Reason
          <input
            className="mt-1 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2.5 dark:bg-black/20"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
          />
        </label>

        <button
          type="submit"
          disabled={booking || !doctorId || !specialty}
          className="mt-5 rounded-full bg-sea px-5 py-2.5 font-semibold text-white disabled:opacity-50"
        >
          {booking ? "Booking…" : "Book appointment"}
        </button>
        {message && <p className="mt-3 text-sm text-sea">{message}</p>}
        {error && <p className="mt-3 text-sm text-red-600 dark:text-red-400">{error}</p>}
      </form>

      <div className="glass rounded-3xl p-6 shadow-soft">
        <h2 className="font-display text-xl font-semibold">Your appointments</h2>
        <ul className="mt-4 space-y-3">
          {appointments.map((a) => {
            const doc = doctors.find((d) => d.id === a.doctor_id);
            return (
              <li key={a.id} className="rounded-2xl bg-white/50 p-3 text-sm dark:bg-white/5">
                {doc ? `${doc.full_name} (${doc.specialty})` : `Doctor #${a.doctor_id}`} ·{" "}
                {new Date(a.scheduled_at).toLocaleString()} · {a.status}
              </li>
            );
          })}
          {appointments.length === 0 && <li className="text-sm opacity-70">No appointments yet.</li>}
        </ul>
      </div>
    </div>
  );
}
