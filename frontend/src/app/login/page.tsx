"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { useDispatch } from "react-redux";
import { api } from "@/lib/api";
import { setAuth } from "@/store";

export default function LoginPage() {
  const router = useRouter();
  const dispatch = useDispatch();
  const [email, setEmail] = useState("patient@example.com");
  const [password, setPassword] = useState("Patient@12345");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const tokens = await api.login(email, password);
      const auth = {
        accessToken: tokens.access_token,
        refreshToken: tokens.refresh_token,
        roles: tokens.roles || [],
        email,
      };
      dispatch(setAuth(auth));
      try {
        const prev = JSON.parse(localStorage.getItem("aihc-auth") || "{}");
        localStorage.setItem("aihc-auth", JSON.stringify({ ...prev, ...auth }));
      } catch {
        localStorage.setItem("aihc-auth", JSON.stringify(auth));
      }
      router.replace("/dashboard");
    } catch (err: any) {
      const msg = err?.message || "Login failed";
      setError(msg === "Failed to fetch" ? "Cannot reach API at 127.0.0.1:8000. Is the backend running?" : msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-md animate-rise glass rounded-3xl p-8 shadow-soft">
      <h1 className="font-display text-3xl font-semibold">Welcome back</h1>
      <p className="mt-2 text-sm opacity-70">Demo: patient@example.com / Patient@12345</p>
      <form onSubmit={onSubmit} className="mt-6 space-y-4">
        <label className="block text-sm">
          Email
          <input
            className="mt-1 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2 dark:bg-black/20"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            type="email"
            required
          />
        </label>
        <label className="block text-sm">
          Password
          <input
            className="mt-1 w-full rounded-xl border border-[var(--line)] bg-white/70 px-3 py-2 dark:bg-black/20"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            required
          />
        </label>
        {error && <p className="text-sm text-coral">{error}</p>}
        <button
          disabled={loading}
          className="w-full rounded-full bg-sea px-4 py-2.5 font-semibold text-white disabled:opacity-60"
        >
          {loading ? "Signing in…" : "Sign in"}
        </button>
      </form>
      <p className="mt-4 text-sm opacity-70">
        New here? <Link href="/register" className="text-sea underline">Register</Link>
      </p>
    </div>
  );
}
