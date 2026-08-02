"use client";

import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { AppLink } from "@/components/AppLink";
import { api } from "@/lib/api";
import { STAT_LINKS } from "@/lib/nav";
import { RootState } from "@/store";

const actions = [
  { href: "/chat", label: "AI Chat", task: "Ask master agent" },
  { href: "/appointments", label: "Appointments", task: "Book / view visits" },
  { href: "/prescriptions", label: "Prescriptions", task: "Analyze Rx text" },
  { href: "/labs", label: "Lab reports", task: "Analyze lab values" },
  { href: "/reminders", label: "Reminders", task: "Schedule medicines" },
  { href: "/symptoms", label: "Symptom check", task: "Run triage" },
  { href: "/telemedicine", label: "Telemedicine", task: "Start virtual visit" },
  { href: "/insurance", label: "Insurance", task: "Check coverage" },
  { href: "/nutrition", label: "Nutrition", task: "Diet & BMI plan" },
  { href: "/emergency", label: "Emergency", task: "Escalate red flags" },
  { href: "/follow-up", label: "Follow-up", task: "Plan next care step" },
  { href: "/notifications", label: "Notifications", task: "View alerts" },
];

function statHref(name: string): string {
  const key = name.toLowerCase().replace(/\s+/g, "_");
  return STAT_LINKS[key]?.href || "/modules";
}

export default function PatientPortalPage() {
  const token = useSelector((s: RootState) => s.auth.accessToken);
  const email = useSelector((s: RootState) => s.auth.email);
  const [dash, setDash] = useState<any>(null);

  useEffect(() => {
    if (!token) return;
    api.dashboard(token).then(setDash).catch(() => undefined);
  }, [token]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-4xl font-semibold">Patient Portal</h1>
        <p className="mt-2 opacity-70">
          Welcome {email}. Open a care task below — each card opens the module and loads its workflow.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {Object.entries(dash?.stats || {}).map(([k, v]) => (
          <AppLink key={k} href={statHref(k)} className="glass rounded-3xl p-5 transition hover:-translate-y-0.5">
            <p className="text-sm uppercase opacity-60">{k}</p>
            <p className="mt-2 font-display text-3xl">{String(v)}</p>
            <p className="mt-2 text-xs font-semibold text-sea">Open →</p>
          </AppLink>
        ))}
      </div>

      <div className="glass rounded-3xl p-5">
        <div className="flex items-center justify-between">
          <h2 className="font-display text-xl font-semibold">Health summary</h2>
          <AppLink href="/symptoms" className="text-sm text-sea underline">
            Run health check
          </AppLink>
        </div>
        <ul className="mt-3 grid gap-2 text-sm sm:grid-cols-2">
          {Object.entries(dash?.health_summary || {}).map(([k, v]) => (
            <li key={k} className="rounded-2xl bg-white/50 p-3 dark:bg-white/5">
              <span className="opacity-60">{k}: </span>
              {String(v ?? "—")}
            </li>
          ))}
          {!Object.keys(dash?.health_summary || {}).length && (
            <li className="opacity-60">No summary yet — try Symptom Checker or upload labs.</li>
          )}
        </ul>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {actions.map((a) => (
          <AppLink
            key={a.href}
            href={a.href}
            className="rounded-2xl bg-sea px-4 py-3 text-white shadow-soft transition hover:-translate-y-0.5"
          >
            <p className="font-semibold">{a.label}</p>
            <p className="text-xs text-white/80">{a.task}</p>
          </AppLink>
        ))}
      </div>

      <AppLink href="/dashboard" className="text-sea underline">
        Open full dashboard
      </AppLink>
    </div>
  );
}
