"use client";

import { useSelector } from "react-redux";
import { AppLink } from "@/components/AppLink";
import { APP_MODULES } from "@/lib/modules";
import { RootState } from "@/store";

export default function ModulesPage() {
  const roles = useSelector((s: RootState) => s.auth.roles);
  const role = (roles[0] || "patient") as "patient" | "doctor" | "admin" | "receptionist";

  const modules = APP_MODULES.filter(
    (m) => m.roles.includes("all") || m.roles.includes(role)
  );

  return (
    <div className="space-y-6">
      <div className="animate-rise">
        <h1 className="font-display text-4xl font-semibold">Major Modules</h1>
        <p className="mt-2 max-w-2xl opacity-70">
          Enterprise care workflows for patients, doctors, and hospital operations.
          AI outputs are assistive only — never a definitive diagnosis.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {modules.map((m, idx) => (
          <AppLink
            key={m.id}
            href={m.href}
            className="glass animate-rise rounded-3xl p-5 shadow-soft transition hover:-translate-y-0.5"
            style={{ animationDelay: `${idx * 40}ms` }}
          >
            <h2 className="font-display text-xl font-semibold">{m.name}</h2>
            <p className="mt-2 text-sm opacity-70">{m.description}</p>
            <p className="mt-4 text-sm font-semibold text-sea">Open module →</p>
          </AppLink>
        ))}
      </div>
    </div>
  );
}
