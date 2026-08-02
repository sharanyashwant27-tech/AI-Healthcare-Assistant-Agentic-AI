"use client";

import Link from "next/link";
import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  type ComponentProps,
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

type AppLinkProps = Omit<ComponentProps<typeof Link>, "href"> & {
  href: string;
  /** Optional task to run before/after navigation (e.g. trigger workflow). */
  onNavigate?: () => void | Promise<void>;
};

/** Site-wide link that uses instant panel switching when available. */
export function AppLink({ href, onClick, onNavigate, children, ...rest }: AppLinkProps) {
  const navigate = usePanelNavigate();

  const handleClick = useCallback(
    async (e: MouseEvent<HTMLAnchorElement>) => {
      onClick?.(e);
      if (e.defaultPrevented) return;
      if (onNavigate) {
        try {
          await onNavigate();
        } catch {
          /* allow navigation even if task fails */
        }
      }
      if (navigate && isNavHref(href)) {
        e.preventDefault();
        void loadPanel(href);
        navigate(href);
      }
    },
    [href, navigate, onClick, onNavigate]
  );

  return (
    <Link href={href} onClick={handleClick} {...rest}>
      {children}
    </Link>
  );
}

export function useAppNavigate() {
  const ctx = usePanelNavigate();
  return useMemo(
    () => ({
      go: (href: string) => {
        if (ctx) ctx(href);
        else if (typeof window !== "undefined") window.location.href = href;
      },
    }),
    [ctx]
  );
}
