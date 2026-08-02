"use client";

import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { AppLink } from "@/components/AppLink";
import { api } from "@/lib/api";
import { RootState } from "@/store";

type Workflow = {
  id: string;
  name: string;
  webhook_path: string;
  steps: string[];
  description: string;
};

/** Related in-app module for each workflow card. */
const WORKFLOW_LINKS: Record<string, { href: string; label: string }> = {
  "patient-registration": { href: "/register", label: "Registration" },
  "appointment-booking": { href: "/appointments", label: "Appointments" },
  emergency: { href: "/emergency", label: "Emergency assistant" },
  "emergency-alert": { href: "/emergency", label: "Emergency assistant" },
  prescription: { href: "/prescriptions", label: "Prescription analyzer" },
  "prescription-ocr": { href: "/prescriptions", label: "Prescription analyzer" },
  "lab-report": { href: "/labs", label: "Lab analyzer" },
  "lab-report-ocr": { href: "/labs", label: "Lab analyzer" },
  "medicine-reminder": { href: "/reminders", label: "Reminders" },
  "insurance-validation": { href: "/insurance", label: "Insurance" },
  "push-notification": { href: "/notifications", label: "Notifications" },
  "sms-notification": { href: "/notifications", label: "Notifications" },
  "email-notification": { href: "/notifications", label: "Notifications" },
};

export default function WorkflowsPage() {
  const token = useSelector((s: RootState) => s.auth.accessToken);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [triggering, setTriggering] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) return;
    api.workflows(token).then((data) => setWorkflows(data.workflows || [])).catch(() => setWorkflows([]));
  }, [token]);

  async function onTrigger(id: string) {
    if (!token) return;
    setTriggering(id);
    setError("");
    try {
      setLastResult(await api.triggerWorkflow(token, id, { source: "ui" }));
    } catch (err: any) {
      setError(err.message || "Trigger failed");
    } finally {
      setTriggering(null);
    }
  }

  return (
    <div className="space-y-6">
      <div className="glass rounded-3xl p-6 shadow-soft">
        <h1 className="font-display text-3xl font-semibold">n8n Workflows</h1>
        <p className="mt-2 text-sm opacity-70">
          Trigger a pipeline, or open the related module to run the care task in-app.
        </p>
      </div>

      {error && <p className="text-sm text-coral">{error}</p>}

      <div className="grid gap-4 lg:grid-cols-2">
        {workflows.map((wf, idx) => {
          const related = WORKFLOW_LINKS[wf.id] || WORKFLOW_LINKS[wf.webhook_path];
          return (
            <article key={wf.id} className="glass rounded-3xl p-6 shadow-soft">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-xs uppercase tracking-wide opacity-50">Workflow {idx + 1}</p>
                  <h2 className="font-display text-xl font-semibold">{wf.name}</h2>
                  <p className="mt-1 text-sm opacity-70">{wf.description}</p>
                  <p className="mt-2 text-xs opacity-50">Webhook: /{wf.webhook_path}</p>
                </div>
                <div className="flex shrink-0 flex-col gap-2">
                  <button
                    type="button"
                    onClick={() => onTrigger(wf.id)}
                    disabled={triggering === wf.id}
                    className="rounded-full bg-sea px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
                  >
                    {triggering === wf.id ? "…" : "Trigger"}
                  </button>
                  {related && (
                    <AppLink
                      href={related.href}
                      className="rounded-full border border-[var(--line)] px-4 py-2 text-center text-sm font-semibold"
                    >
                      Open {related.label}
                    </AppLink>
                  )}
                </div>
              </div>
              <ol className="mt-4 flex flex-wrap items-center gap-2 text-sm">
                {wf.steps.map((step, i) => (
                  <li key={step} className="flex items-center gap-2">
                    <span className="rounded-full border border-[var(--line)] bg-white/60 px-3 py-1 dark:bg-black/20">
                      {step}
                    </span>
                    {i < wf.steps.length - 1 ? <span className="opacity-40">↓</span> : null}
                  </li>
                ))}
              </ol>
            </article>
          );
        })}
      </div>

      {lastResult ? (
        <pre className="glass overflow-auto rounded-3xl p-4 text-xs shadow-soft">
          {JSON.stringify(lastResult, null, 2)}
        </pre>
      ) : null}
    </div>
  );
}
