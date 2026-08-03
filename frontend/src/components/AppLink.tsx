"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  type AnchorHTMLAttributes,
  type MouseEvent,
  type ReactNode,
} from "react";
import { isNavHref, loadPanel } from "@/lib/panels";

type NavigateFn = (href: string) => void;

const PanelNavContext = createContext<NavigateFn | null>(null);

export function PanelNavProvider({
  navigate,
  children,
}: {
  navigate: NavigateFn;
  children: ReactNode;
}) {
  return <PanelNavContext.Provider value={navigate}>{children}</PanelNavContext.Provider>;
}

export function usePanelNavigate() {
  return useContext(PanelNavContext);
}

type AppLinkProps = AnchorHTMLAttributes<HTMLAnchorElement> & {
  href: string;
  /** Optional task to run when the link is activated. */
  onNavigate?: () => void | Promise<void>;
};

/**
 * Site-wide link that uses Shell panel navigation when available.
 * Uses a plain <a> so Next.js Link soft-nav cannot swallow / ignore the click.
 */
export function AppLink({ href, onClick, onNavigate, children, className, ...rest }: AppLinkProps) {
  const navigate = usePanelNavigate();

  const handleClick = useCallback(
    (e: MouseEvent<HTMLAnchorElement>) => {
      onClick?.(e);
      if (e.defaultPrevented) return;

      // Always take over same-origin app routes so cards respond immediately.
      if (href.startsWith("/") && !href.startsWith("//")) {
        e.preventDefault();
        void (async () => {
          if (onNavigate) {
            try {
              await onNavigate();
            } catch {
              /* still navigate */
            }
          }
          if (navigate) {
            if (isNavHref(href)) void loadPanel(href);
            navigate(href);
            return;
          }
          window.location.assign(href);
        })();
      }
    },
    [href, navigate, onClick, onNavigate]
  );

  return (
    <a href={href} onClick={handleClick} className={className} {...rest}>
      {children}
    </a>
  );
}

export function useAppNavigate() {
  const ctx = usePanelNavigate();
  return useMemo(
    () => ({
      go: (href: string) => {
        if (ctx) ctx(href);
        else if (typeof window !== "undefined") window.location.assign(href);
      },
    }),
    [ctx]
  );
}
