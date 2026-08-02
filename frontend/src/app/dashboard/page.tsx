"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { AppLink } from "@/components/AppLink";
import { api } from "@/lib/api";
import { STAT_LINKS } from "@/lib/nav";
import { RootState } from "@/store";

const DashboardChart = dynamic(
  () => import("@/components/DashboardChart").then((m) => m.DashboardChart),
  {
    ssr: false,
    loading: () => <div className="h-full animate-pulse rounded-2xl bg-white/40 dark:bg-white/5" />,
  }
);

const QUICK_ACTIONS = [
  { href: "/chat", label: "AI Chat", task: "Ask the master agent" },
  { href: "/symptoms", label: "Symptom check", task: "Run triage analysis" },
  { href: "/appointments", label: "Book visit", task: "Create appointment" },
  { href: "/prescriptions", label: "Analyze Rx", task: "Extract & check meds" },
  { href: "/labs", label: "Lab analyzer", task: "Flag abnormal values" },
  { href: "/emergency", label: "Emergency", task: "Escalate red flags" },
  { href: "/telemedicine", label: "Telemedicine", task: "Start virtual visit" },
  { href: "/workflows", label: "Workflows", task: "Trigger n8n pipeline" },
  { href: "/nutrition", label: "Nutrition", task: "BMI & diet plan" },
  { href: "/knowledge", label: "Knowledge", task: "Guideline retrieval" },
  { href: "/reminders", label: "Reminders", task: "Schedule medicines" },
  { href: "/notifications", label: "Alerts", task: "View notifications" },
];

function statHref(name: string): string {
  const key = name.toLowerCase().replace(/\s+/g, "_");
  return STAT_LINKS[key]?.href || STAT_LINKS[name.toLowerCase()]?.href || "/modules";
}

export default function DashboardPage() {
  const token = useSelector((s: RootState) => s.auth.accessToken);
  const roles = useSelector((s: RootState) => s.auth.roles);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) return;
    api
      .dashboard(token)
      .then(setData)
      .catch((e) => setError(e.message));
  }, [token]);

  const role = data?.role || roles[0] || "patient";
  const title =
    role === "doctor"
      ? "Doctor Dashboard"
      : role === "admin"
        ? "Admin Dashboard"
        : "Patient Dashboard";

  const chartData = Object.entries(data?.stats || {}).map(([name, value]) => ({
    name,
    value: Number(value),
  }));

  return (
    <div className="space-y-6">
      <div className="animate-rise">
        <h1 className="font-display text-4xl font-semibold">{title}</h1>
        <p className="mt-2 max-w-2xl opacity-70">
          {(data?.features || []).join(" · ") || "Role-aware care overview"}
        </p>
      </div>

      {error && <p className="text-coral">{error}</p>}

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {QUICK_ACTIONS.map((a) => (
          <AppLink
            key={a.href}
            href={a.href}
            className="glass rounded-3xl p-4 shadow-soft transition hover:-translate-y-0.5"
          >
            <p className="font-display text-lg font-semibold">{a.label}</p>
            <p className="mt-1 text-xs opacity-60">{a.task}</p>
          </AppLink>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        {chartData.map((item, idx) => (
          <AppLink
            key={item.name}
            href={statHref(item.name)}
            className="glass animate-rise rounded-3xl p-5 shadow-soft transition hover:-translate-y-0.5"
            style={{ animationDelay: `${idx * 80}ms` }}
          >
            <p className="text-sm uppercase tracking-wide opacity-60">{item.name}</p>
            <p className="mt-2 font-display text-3xl font-semibold">{item.value}</p>
            <p className="mt-2 text-xs font-semibold text-sea">Open →</p>
          </AppLink>
        ))}
      </div>

      {role === "patient" && (
        <div className="grid gap-6 lg:grid-cols-3">
          <Section title="Health summary" href="/portal/patient">
            <KV data={data?.health_summary || {}} />
            <AppLink href="/chat" className="mt-4 inline-block text-sea underline">
              Start AI Chat
            </AppLink>
          </Section>
          <Section title="Appointments" href="/appointments">
            <List
              items={(data?.appointments || []).map(
                (a: any) => `${new Date(a.scheduled_at).toLocaleString()} · ${a.status}`
              )}
            />
          </Section>
          <Section title="Prescriptions" href="/prescriptions">
            <List
              items={(data?.prescriptions || []).map(
                (p: any) => `#${p.id} · ${p.dosage || "see Rx"} · ${p.duration || ""}`
              )}
            />
          </Section>
          <Section title="Reports" href="/labs">
            <List
              items={(data?.reports || []).map(
                (r: any) => `${r.report_type}: ${r.summary || "uploaded"}`
              )}
            />
          </Section>
          <Section title="Medication reminders" href="/reminders">
            <List items={(data?.reminders || []).map((r: any) => r.title || r.message)} />
          </Section>
          <Section title="Notifications" href="/notifications">
            <List items={(data?.notifications || []).map((n: any) => n.title)} />
          </Section>
        </div>
      )}

      {role === "doctor" && (
        <div className="grid gap-6 lg:grid-cols-2">
          <Section title="Patient queue" href="/appointments">
            <List
              items={(data?.patient_queue || []).map(
                (q: any) =>
                  `Patient #${q.patient_id} · ${new Date(q.scheduled_at).toLocaleString()} · ${q.status}`
              )}
            />
          </Section>
          <Section title="AI summaries" href="/chat">
            <List
              items={(data?.ai_summaries || []).map((s: any) => `${s.title}: ${s.summary}`)}
            />
          </Section>
          <Section title="Risk alerts" href="/emergency">
            <List items={(data?.risk_alerts || []).map((a: any) => `[${a.level}] ${a.message}`)} />
          </Section>
          <Section title="Lab insights" href="/labs">
            <List
              items={(data?.lab_insights || []).map(
                (l: any) => `P#${l.patient_id} · ${l.report_type}: ${l.summary || "n/a"}`
              )}
            />
          </Section>
          <Section title="Clinical notes" href="/knowledge">
            <List items={(data?.clinical_notes || []).map((n: any) => `${n.title}: ${n.message}`)} />
          </Section>
          <Section title="HITL / workflows" href="/workflows">
            <p className="opacity-70">Review high-risk AI drafts and trigger care pipelines.</p>
          </Section>
        </div>
      )}

      {role === "admin" && (
        <div className="grid gap-6 lg:grid-cols-2">
          <Section title="Hospital analytics" href="/portal/admin">
            <KV data={data?.hospital_analytics || {}} />
          </Section>
          <Section title="AI usage" href="/modules">
            <p className="text-sm opacity-80">{data?.ai_usage?.note}</p>
            <List items={data?.ai_usage?.modules || []} />
          </Section>
          <Section title="Appointment statistics" href="/appointments">
            <KV data={data?.appointment_statistics?.by_status || { total: data?.appointment_statistics?.total }} />
          </Section>
          <Section title="Operational metrics" href="/notifications">
            <KV
              data={{
                active_users: data?.operational_metrics?.active_users,
                notifications_open: data?.operational_metrics?.notifications_open,
                services: (data?.operational_metrics?.services || []).join(", "),
              }}
            />
          </Section>
          <div className="glass animate-drift rounded-3xl p-5 shadow-soft lg:col-span-2">
            <div className="flex items-center justify-between">
              <h2 className="font-display text-xl font-semibold">Activity</h2>
              <AppLink href="/workflows" className="text-sm text-sea underline">
                Run workflows
              </AppLink>
            </div>
            <div className="mt-4 h-64">
              <DashboardChart data={chartData} />
            </div>
          </div>
        </div>
      )}

      <div className="rounded-2xl border border-coral/30 bg-coral/10 p-4 text-sm">
        {(data?.alerts || []).join(" ") ||
          "Not a diagnosis. For emergencies, call local emergency services."}
      </div>
    </div>
  );
}

function Section({
  title,
  href,
  children,
}: {
  title: string;
  href: string;
  children: React.ReactNode;
}) {
  return (
    <div className="glass rounded-3xl p-5 shadow-soft">
      <div className="flex items-center justify-between gap-3">
        <h2 className="font-display text-xl font-semibold">{title}</h2>
        <AppLink href={href} className="text-xs font-semibold text-sea">
          Open →
        </AppLink>
      </div>
      <div className="mt-3 text-sm">{children}</div>
    </div>
  );
}

function List({ items }: { items: string[] }) {
  if (!items.length) return <p className="opacity-60">No items yet.</p>;
  return (
    <ul className="space-y-2">
      {items.map((item, i) => (
        <li key={i} className="rounded-2xl bg-white/50 p-3 dark:bg-white/5">
          {item}
        </li>
      ))}
    </ul>
  );
}

function KV({ data }: { data: Record<string, unknown> }) {
  const entries = Object.entries(data || {}).filter(([, v]) => v !== undefined && v !== null);
  if (!entries.length) return <p className="opacity-60">No data.</p>;
  return (
    <dl className="space-y-2">
      {entries.map(([k, v]) => (
        <div key={k} className="flex justify-between gap-3 rounded-2xl bg-white/50 px-3 py-2 dark:bg-white/5">
          <dt className="opacity-60">{k}</dt>
          <dd className="font-medium">{String(v)}</dd>
        </div>
      ))}
    </dl>
  );
}
