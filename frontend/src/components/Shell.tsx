"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, type ComponentType, type MouseEvent } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Moon, Sun, LogOut, Activity, Menu, X } from "lucide-react";
import { PanelNavProvider } from "@/components/AppLink";
import { NAV_LINKS, publicPaths } from "@/lib/nav";
import { getCachedPanel, isNavHref, loadPanel, preloadAllPanels } from "@/lib/panels";
import { logout, RootState, toggleDarkMode } from "@/store";

export function Shell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const dispatch = useDispatch();
  const { accessToken, email, darkMode, roles } = useSelector((s: RootState) => s.auth);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [panelHref, setPanelHref] = useState(pathname);
  const [Panel, setPanel] = useState<ComponentType | null>(() => getCachedPanel(pathname));
  const [loadingPanel, setLoadingPanel] = useState(false);

  useEffect(() => {
    if (!accessToken && !publicPaths.has(pathname)) {
      router.replace("/login");
    }
  }, [accessToken, pathname, router]);

  useEffect(() => {
    setMobileOpen(false);
    setPanelHref(pathname);
    if (!isNavHref(pathname)) {
      setPanel(null);
      setLoadingPanel(false);
      return;
    }
    const cached = getCachedPanel(pathname);
    if (cached) {
      setPanel(() => cached);
      setLoadingPanel(false);
      return;
    }
    setLoadingPanel(true);
    loadPanel(pathname).then((comp) => {
      setPanel(() => comp);
      setLoadingPanel(false);
    });
  }, [pathname]);

  const showNav = Boolean(accessToken) && !publicPaths.has(pathname);

  useEffect(() => {
    if (!showNav) return;
    preloadAllPanels();
  }, [showNav]);

  function openPanel(href: string, e?: MouseEvent<HTMLAnchorElement>) {
    e?.preventDefault();
    if (!isNavHref(href)) {
      router.push(href);
      return;
    }
    if (href === panelHref && Panel && !loadingPanel) return;

    setMobileOpen(false);
    setPanelHref(href);

    const cached = getCachedPanel(href);
    if (cached) {
      setPanel(() => cached);
      setLoadingPanel(false);
      if (window.location.pathname !== href) {
        window.history.pushState({ panel: href }, "", href);
      }
      return;
    }

    setLoadingPanel(true);
    loadPanel(href).then((comp) => {
      setPanel(() => comp);
      setLoadingPanel(false);
      if (window.location.pathname !== href) {
        window.history.pushState({ panel: href }, "", href);
      }
    });
  }

  useEffect(() => {
    function onPopState() {
      const href = window.location.pathname;
      setPanelHref(href);
      if (!isNavHref(href)) {
        setPanel(null);
        setLoadingPanel(false);
        return;
      }
      const cached = getCachedPanel(href);
      if (cached) {
        setPanel(() => cached);
        setLoadingPanel(false);
      } else {
        setLoadingPanel(true);
        loadPanel(href).then((comp) => {
          setPanel(() => comp);
          setLoadingPanel(false);
        });
      }
    }
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  const navItems = (
    <nav className="flex flex-col gap-1 p-3">
      {NAV_LINKS.map((l) => {
        const active = panelHref === l.href || panelHref.startsWith(l.href + "/");
        return (
          <Link
            key={l.href}
            href={l.href}
            prefetch={false}
            onClick={(e) => openPanel(l.href, e)}
            onMouseEnter={() => {
              if (isNavHref(l.href)) void loadPanel(l.href);
            }}
            className={`rounded-xl px-3 py-2 text-sm transition ${
              active
                ? "bg-sea text-white shadow-soft"
                : "text-ink hover:bg-white/70 dark:text-mist dark:hover:bg-white/10"
            }`}
          >
            {l.label}
          </Link>
        );
      })}
    </nav>
  );

  const mainContent = (() => {
    if (!showNav) return children;
    if (loadingPanel) {
      return (
        <div className="animate-pulse space-y-4" aria-label="Loading panel">
          <div className="h-10 w-1/3 rounded-2xl bg-white/50 dark:bg-white/10" />
          <div className="h-4 w-2/3 rounded-xl bg-white/40 dark:bg-white/5" />
          <div className="grid gap-4 md:grid-cols-3">
            <div className="h-28 rounded-3xl bg-white/50 dark:bg-white/10" />
            <div className="h-28 rounded-3xl bg-white/50 dark:bg-white/10" />
            <div className="h-28 rounded-3xl bg-white/50 dark:bg-white/10" />
          </div>
        </div>
      );
    }
    if (Panel) return <Panel />;
    return children;
  })();

  return (
    <PanelNavProvider navigate={(href) => openPanel(href)}>
      <div className="min-h-screen">
        <header className="sticky top-0 z-40 border-b border-[var(--line)] bg-[color:var(--panel)] backdrop-blur-xl">
          <div className="flex items-center justify-between px-4 py-3 md:px-6">
            <div className="flex items-center gap-3">
              {showNav && (
                <button
                  type="button"
                  className="rounded-xl border border-[var(--line)] p-2 lg:hidden"
                  aria-label={mobileOpen ? "Close menu" : "Open menu"}
                  onClick={() => setMobileOpen((v) => !v)}
                >
                  {mobileOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
                </button>
              )}
              <Link
                href={accessToken ? "/modules" : "/"}
                onClick={(e) => {
                  if (accessToken) openPanel("/modules", e);
                }}
                className="flex items-center gap-3"
              >
                <span className="grid h-10 w-10 place-items-center rounded-2xl bg-sea text-white shadow-soft">
                  <Activity className="h-5 w-5" />
                </span>
                <div>
                  <p className="brand-mark font-display text-xl font-semibold text-ink dark:text-mist">
                    AI Healthcare Assistant
                  </p>
                  <p className="hidden text-xs text-slateish/70 dark:text-mist/60 sm:block">
                    Agentic care guidance · not a diagnosis
                  </p>
                </div>
              </Link>
            </div>
            <div className="flex items-center gap-2">
              {email && (
                <span className="hidden text-sm text-slateish/80 dark:text-mist/70 md:inline">
                  {email} · {roles[0] || "user"}
                </span>
              )}
              <button
                aria-label="Toggle dark mode"
                onClick={() => dispatch(toggleDarkMode())}
                className="rounded-xl border border-[var(--line)] p-2 hover:bg-white/40 dark:hover:bg-white/5"
              >
                {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
              </button>
              {accessToken && (
                <button
                  onClick={() => {
                    dispatch(logout());
                    router.push("/login");
                  }}
                  className="rounded-xl border border-[var(--line)] p-2 hover:bg-white/40 dark:hover:bg-white/5"
                  aria-label="Sign out"
                >
                  <LogOut className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>
        </header>

        {showNav ? (
          <div className="mx-auto flex min-h-[calc(100vh-4.5rem)] max-w-[90rem]">
            <aside className="sticky top-[4.5rem] hidden h-[calc(100vh-4.5rem)] w-60 shrink-0 overflow-y-auto border-r border-[var(--line)] bg-[color:var(--panel)] backdrop-blur-xl lg:block">
              <p className="px-4 pt-4 text-xs font-semibold uppercase tracking-wide opacity-50">
                Navigation
              </p>
              {navItems}
            </aside>

            {mobileOpen && (
              <div className="fixed inset-0 z-50 lg:hidden">
                <button
                  type="button"
                  className="absolute inset-0 bg-ink/40"
                  aria-label="Close menu overlay"
                  onClick={() => setMobileOpen(false)}
                />
                <aside className="absolute left-0 top-0 h-full w-72 overflow-y-auto border-r border-[var(--line)] bg-[color:var(--panel)] shadow-soft backdrop-blur-xl">
                  <div className="flex items-center justify-between border-b border-[var(--line)] px-4 py-3">
                    <p className="font-display text-lg font-semibold">Menu</p>
                    <button
                      type="button"
                      className="rounded-xl border border-[var(--line)] p-2"
                      aria-label="Close menu"
                      onClick={() => setMobileOpen(false)}
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                  {navItems}
                </aside>
              </div>
            )}

            <main className="min-w-0 flex-1 px-4 py-6 md:px-8 md:py-10">{mainContent}</main>
          </div>
        ) : (
          <main className="mx-auto max-w-7xl px-4 py-6 md:px-8 md:py-10">{children}</main>
        )}
      </div>
    </PanelNavProvider>
  );
}
