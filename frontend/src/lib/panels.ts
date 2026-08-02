"use client";

import type { ComponentType } from "react";
import type { NavHref } from "@/lib/nav";
import { NAV_LINKS } from "@/lib/nav";

type PanelModule = { default: ComponentType };

const loaders: Record<NavHref, () => Promise<PanelModule>> = {
  "/modules": () => import("@/app/modules/page"),
  "/dashboard": () => import("@/app/dashboard/page"),
  "/portal/patient": () => import("@/app/portal/patient/page"),
  "/portal/doctor": () => import("@/app/portal/doctor/page"),
  "/portal/admin": () => import("@/app/portal/admin/page"),
  "/chat": () => import("@/app/chat/page"),
  "/symptoms": () => import("@/app/symptoms/page"),
  "/appointments": () => import("@/app/appointments/page"),
  "/telemedicine": () => import("@/app/telemedicine/page"),
  "/knowledge": () => import("@/app/knowledge/page"),
  "/prescriptions": () => import("@/app/prescriptions/page"),
  "/imaging": () => import("@/app/imaging/page"),
  "/labs": () => import("@/app/labs/page"),
  "/nutrition": () => import("@/app/nutrition/page"),
  "/reminders": () => import("@/app/reminders/page"),
  "/follow-up": () => import("@/app/follow-up/page"),
  "/insurance": () => import("@/app/insurance/page"),
  "/emergency": () => import("@/app/emergency/page"),
  "/workflows": () => import("@/app/workflows/page"),
  "/notifications": () => import("@/app/notifications/page"),
};

const cache = new Map<string, ComponentType>();
const inflight = new Map<string, Promise<ComponentType>>();

export function isNavHref(href: string): href is NavHref {
  return Object.prototype.hasOwnProperty.call(loaders, href);
}

export function getCachedPanel(href: string): ComponentType | null {
  return cache.get(href) || null;
}

export function loadPanel(href: NavHref): Promise<ComponentType> {
  const hit = cache.get(href);
  if (hit) return Promise.resolve(hit);
  const existing = inflight.get(href);
  if (existing) return existing;
  const promise = loaders[href]()
    .then((mod) => {
      cache.set(href, mod.default);
      inflight.delete(href);
      return mod.default;
    })
    .catch((err) => {
      inflight.delete(href);
      throw err;
    });
  inflight.set(href, promise);
  return promise;
}

/** Preload every sidebar panel in parallel (used after login). */
export function preloadAllPanels(): void {
  for (const link of NAV_LINKS) {
    void loadPanel(link.href);
  }
}
