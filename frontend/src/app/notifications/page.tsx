"use client";

import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { api } from "@/lib/api";
import { RootState } from "@/store";

export default function NotificationsPage() {
  const token = useSelector((s: RootState) => s.auth.accessToken);
  const [items, setItems] = useState<any[]>([]);

  async function refresh() {
    if (!token) return;
    setItems(await api.notifications(token));
  }

  useEffect(() => {
    refresh().catch(() => undefined);
  }, [token]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-display text-4xl font-semibold">Notification Center</h1>
          <p className="mt-2 opacity-70">Reminders, telemedicine alerts, and emergency notices.</p>
        </div>
        <button
          className="rounded-full bg-sea px-5 py-2.5 font-semibold text-white"
          onClick={async () => {
            if (!token) return;
            await api.markAllNotificationsRead(token);
            await refresh();
          }}
        >
          Mark all read
        </button>
      </div>
      <ul className="space-y-3">
        {items.map((n) => (
          <li
            key={n.id}
            className={`glass rounded-3xl p-4 ${n.is_read ? "opacity-70" : ""}`}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs uppercase opacity-60">{n.channel}</p>
                <p className="font-display text-lg font-semibold">{n.title}</p>
                <p className="mt-1 text-sm opacity-80">{n.message}</p>
              </div>
              {!n.is_read && token && (
                <button
                  className="rounded-full border border-[var(--line)] px-3 py-1 text-xs"
                  onClick={async () => {
                    await api.markNotificationRead(token, n.id);
                    await refresh();
                  }}
                >
                  Mark read
                </button>
              )}
            </div>
          </li>
        ))}
        {items.length === 0 && <li className="opacity-70">No notifications yet.</li>}
      </ul>
    </div>
  );
}
