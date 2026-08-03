"use client";

import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { AppLink } from "@/components/AppLink";
import { api } from "@/lib/api";
import { STAT_LINKS } from "@/lib/nav";
import { RootState } from "@/store";

const actions = [
  { href: "/dashboard", label: "Analytics dashboard", task: "Stats & charts" },
  { href: "/workflows", label: "n8n workflows", task: "Trigger pipelines" },
  { href: "/appointments", label: "Appointments", task: "Hospital schedule" },
  { href: "/notifications", label: "Notifications", task: "Ops alerts" },
  { href: "/modules", label: "All modules", task: "Module catalog" },
  { href: "/portal/doctor", label: "Doctor portal", task: "Clinician workspace" },
  { href: "/portal/patient", label: "Patient portal", task: "Patient workspace" },
  { href: "/emergency", label: "Emergency desk", task: "Escalation flow" },
  { href: "/telemedicine", label: "Telemedicine", task: "Virtual rooms" },
  { href: "/chat", label: "AI assistant", task: "Admin Q&A" },
  { href: "/knowledge", label: "Knowledge base", task: "Guideline RAG" },
  { href: "/labs", label: "Lab reports", task: "Hospital labs" },
];

function statHref(name: string): string {
  const key = name.toLowerCase().replace(/\s+/g, "_");
  return STAT_LINKS[key]?.href || STAT_LINKS[name.toLowerCase()]?.href || "/modules";
}

export default function HospitalAdminPage() {
  const token = useSelector((s: RootState) => s.auth.accessToken);
  const [dash, setDash] = useState<any>(null);
  const [security, setSecurity] = useState<any>(null);

  useEffect(() => {
    if (!token) return;
    Promise.all([api.dashboard(token), api.security(token)])
      .then(([d, s]) => {
        setDash(d);
        setSecurity(s);
      })
      .catch(() => undefined);
  }, [token]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-4xl font-semibold">Admin Portal</h1>
        <p className="mt-2 opacity-70">
          Hospital operations — click any card to open the related module.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        {Object.entries(dash?.stats || {}).map(([k, v]) => (
          <AppLink
            key={k}
            href={statHref(k)}
            className="glass block cursor-pointer rounded-3xl p-5 transition hover:-translate-y-0.5 hover:ring-2 hover:ring-sea/40"
          >
            <p className="text-sm uppercase opacity-60">{k}</p>
            <p className="mt-2 font-display text-3xl">{String(v)}</p>
            <p className="mt-2 text-xs font-semibold text-sea">Open {statHref(k)} →</p>
          </AppLink>
        ))}
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {actions.map((a) => (
          <AppLink
            key={a.href + a.label}
            href={a.href}
            className="block cursor-pointer rounded-2xl bg-sea px-4 py-3 text-white shadow-soft transition hover:-translate-y-0.5 hover:brightness-110"
          >
            <p className="font-semibold">{a.label}</p>
            <p className="text-xs text-white/80">{a.task}</p>
          </AppLink>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Panel title="Hospital analytics" href="/dashboard" obj={dash?.hospital_analytics} />
        <div className="glass rounded-3xl p-5">
          <div className="flex items-center justify-between">
            <h2 className="font-display text-xl font-semibold">AI usage</h2>
            <AppLink href="/modules" className="text-xs font-semibold text-sea">
              Modules →
            </AppLink>
          </div>
          <p className="mt-2 text-sm opacity-70">{dash?.ai_usage?.note}</p>
          <ul className="mt-3 flex flex-wrap gap-2 text-sm">
            {(dash?.ai_usage?.modules || []).map((m: string) => (
              <li key={m}>
                <AppLink
                  href="/modules"
                  className="inline-block cursor-pointer rounded-full border border-[var(--line)] px-3 py-1 hover:bg-white/40"
                >
                  {m}
                </AppLink>
              </li>
            ))}
          </ul>
        </div>
        <Panel
          title="Appointment statistics"
          href="/appointments"
          obj={dash?.appointment_statistics?.by_status || { total: dash?.appointment_statistics?.total }}
        />
        <Panel
          title="Operational metrics"
          href="/notifications"
          obj={{
            active_users: dash?.operational_metrics?.active_users,
            notifications_open: dash?.operational_metrics?.notifications_open,
            services: (dash?.operational_metrics?.services || []).join(", "),
          }}
        />
      </div>

      {security && (
        <div className="glass rounded-3xl p-5 text-sm">
          <div className="flex items-center justify-between">
            <h2 className="font-display text-xl font-semibold">Security posture</h2>
            <AppLink href="/workflows" className="text-xs font-semibold text-sea">
              Ops workflows →
            </AppLink>
          </div>
          <ul className="mt-3 grid gap-2 sm:grid-cols-2">
            <li>JWT Authentication: {String(security.jwt_authentication)}</li>
            <li>RBAC: {String(security.rbac)}</li>
            <li>Audit logging: {String(security.audit_logging)}</li>
            <li>PHI masking: {String(security.phi_masking_in_ai_prompts)}</li>
            <li>Encryption: {security.data_encryption?.algorithm}</li>
            <li>Consent management: {String(security.consent_management)}</li>
          </ul>
        </div>
      )}

      <AppLink href="/dashboard" className="text-sea underline">
        Open full dashboard
      </AppLink>
    </div>
  );
}

function Panel({
  title,
  href,
  obj,
}: {
  title: string;
  href: string;
  obj?: Record<string, unknown>;
}) {
  return (
    <div className="glass rounded-3xl p-5">
      <div className="flex items-center justify-between gap-3">
        <h2 className="font-display text-xl font-semibold">{title}</h2>
        <AppLink href={href} className="text-xs font-semibold text-sea">
          Open →
        </AppLink>
      </div>
      <ul className="mt-4 space-y-2 text-sm">
        {Object.entries(obj || {}).map(([k, v]) => (
          <li key={k}>
            <AppLink
              href={href}
              className="flex cursor-pointer justify-between rounded-2xl bg-white/50 p-3 dark:bg-white/5 hover:bg-white/70"
            >
              <span className="opacity-60">{k}</span>
              <span>{String(v)}</span>
            </AppLink>
          </li>
        ))}
        {!Object.keys(obj || {}).length && (
          <li>
            <AppLink href={href} className="block rounded-2xl bg-white/50 p-3 text-sea dark:bg-white/5">
              Open module →
            </AppLink>
          </li>
        )}
      </ul>
    </div>
  );
}
