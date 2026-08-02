"use client";

import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { AppLink } from "@/components/AppLink";
import { api } from "@/lib/api";
import { STAT_LINKS } from "@/lib/nav";
import { RootState } from "@/store";

const actions = [
  { href: "/appointments", label: "Patient queue / appointments", task: "Manage visits" },
  { href: "/chat", label: "AI clinical assistant", task: "Ask with evidence" },
  { href: "/labs", label: "Lab insights", task: "Review reports" },
  { href: "/prescriptions", label: "Prescription analyzer", task: "Check interactions" },
  { href: "/emergency", label: "Risk / emergency", task: "Escalate red flags" },
  { href: "/knowledge", label: "Guidelines", task: "WHO/CDC retrieval" },
  { href: "/telemedicine", label: "Telemedicine", task: "Start session" },
  { href: "/workflows", label: "Care workflows", task: "Trigger n8n" },
  { href: "/follow-up", label: "Follow-up agent", task: "Plan next steps" },
  { href: "/imaging", label: "Imaging assistant", task: "Assistive review" },
];

function statHref(name: string): string {
  const key = name.toLowerCase().replace(/\s+/g, "_");
  return STAT_LINKS[key]?.href || "/appointments";
}

export default function DoctorPortalPage() {
  const token = useSelector((s: RootState) => s.auth.accessToken);
  const [dash, setDash] = useState<any>(null);

  useEffect(() => {
    if (!token) return;
    api.dashboard(token).then(setDash).catch(() => undefined);
  }, [token]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-4xl font-semibold">Doctor Portal</h1>
        <p className="mt-2 opacity-70">
          Clinician workspace — each card opens the module and runs its care task.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        {Object.entries(dash?.stats || {}).map(([k, v]) => (
          <AppLink key={k} href={statHref(k)} className="glass rounded-3xl p-5 transition hover:-translate-y-0.5">
            <p className="text-sm uppercase opacity-60">{k}</p>
            <p className="mt-2 font-display text-3xl">{String(v)}</p>
            <p className="mt-2 text-xs font-semibold text-sea">Open →</p>
          </AppLink>
        ))}
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

      <div className="grid gap-6 lg:grid-cols-2">
        <Panel
          title="Patient queue"
          href="/appointments"
          items={(dash?.patient_queue || []).map(
            (q: any) => `P#${q.patient_id} · ${q.status} · ${q.reason || "visit"}`
          )}
        />
        <Panel
          title="AI summaries"
          href="/chat"
          items={(dash?.ai_summaries || []).map((s: any) => `${s.title}: ${s.summary}`)}
        />
        <Panel
          title="Risk alerts"
          href="/emergency"
          items={(dash?.risk_alerts || []).map((a: any) => a.message)}
        />
        <Panel
          title="Lab insights"
          href="/labs"
          items={(dash?.lab_insights || []).map(
            (l: any) => `${l.report_type}: ${l.summary || "pending review"}`
          )}
        />
        <Panel
          title="Clinical notes"
          href="/knowledge"
          items={(dash?.clinical_notes || []).map((n: any) => `${n.title}: ${n.message}`)}
        />
      </div>

      <AppLink href="/dashboard" className="text-sea underline">
        Open full dashboard
      </AppLink>
    </div>
  );
}

function Panel({ title, href, items }: { title: string; href: string; items: string[] }) {
  return (
    <div className="glass rounded-3xl p-5">
      <div className="flex items-center justify-between gap-3">
        <h2 className="font-display text-xl font-semibold">{title}</h2>
        <AppLink href={href} className="text-xs font-semibold text-sea">
          Open →
        </AppLink>
      </div>
      <ul className="mt-4 space-y-2 text-sm">
        {items.length === 0 && <li className="opacity-70">No items — open module to start a task.</li>}
        {items.map((item, i) => (
          <li key={i}>
            <AppLink href={href} className="block rounded-2xl bg-white/50 p-3 dark:bg-white/5 hover:bg-white/70">
              {item}
            </AppLink>
          </li>
        ))}
      </ul>
    </div>
  );
}
