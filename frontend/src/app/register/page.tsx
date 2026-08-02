"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { api } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    role: "patient",
    specialty: "",
    license_number: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await api.register(form);
      router.push("/login");
    } catch (err: any) {
      setError(err.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-lg animate-rise glass rounded-3xl p-8 shadow-soft">
      <h1 className="font-display text-3xl font-semibold">Create account</h1>
      <form onSubmit={onSubmit} className="mt-6 grid gap-4">
        {(["full_name", "email", "password"] as const).map((key) => (
          <label key={key} className="block text-sm capitalize">
            {key.replace("_", " ")}
            <input
              className="mt-1 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2 dark:bg-black/20"
              type={key === "password" ? "password" : key === "email" ? "email" : "text"}
              value={form[key]}
              onChange={(e) => setForm({ ...form, [key]: e.target.value })}
              required
            />
          </label>
        ))}
        <label className="block text-sm">
          Role
          <select
            className="mt-1 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2 dark:bg-black/20"
            value={form.role}
            onChange={(e) => setForm({ ...form, role: e.target.value })}
          >
            <option value="patient">Patient</option>
            <option value="doctor">Doctor</option>
            <option value="receptionist">Receptionist</option>
            <option value="admin">Admin</option>
          </select>
        </label>
        {form.role === "doctor" && (
          <>
            <input
              placeholder="Specialty"
              className="rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2 dark:bg-black/20"
              value={form.specialty}
              onChange={(e) => setForm({ ...form, specialty: e.target.value })}
            />
            <input
              placeholder="License number"
              className="rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2 dark:bg-black/20"
              value={form.license_number}
              onChange={(e) => setForm({ ...form, license_number: e.target.value })}
            />
          </>
        )}
        {error && <p className="text-sm text-coral">{error}</p>}
        <button disabled={loading} className="rounded-full bg-sea px-4 py-2.5 font-semibold text-white">
          {loading ? "Creating…" : "Register"}
        </button>
      </form>
      <p className="mt-4 text-sm opacity-70">
        Already registered? <Link href="/login" className="text-sea underline">Sign in</Link>
      </p>
    </div>
  );
}
