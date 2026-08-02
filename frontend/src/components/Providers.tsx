"use client";

import { Provider, useDispatch, useSelector } from "react-redux";
import { useEffect } from "react";
import { hydrate, store, RootState } from "@/store";

function ThemeSync({ children }: { children: React.ReactNode }) {
  const darkMode = useSelector((s: RootState) => s.auth.darkMode);
  const dispatch = useDispatch();

  useEffect(() => {
    const raw = localStorage.getItem("aihc-auth");
    if (raw) {
      try {
        dispatch(hydrate(JSON.parse(raw)));
      } catch {
        /* ignore */
      }
    }
  }, [dispatch]);

  useEffect(() => {
    const state = store.getState().auth;
    localStorage.setItem(
      "aihc-auth",
      JSON.stringify({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        roles: state.roles,
        email: state.email,
        darkMode: state.darkMode,
      })
    );
    document.documentElement.classList.toggle("dark", state.darkMode);
  }, [darkMode]);

  useEffect(() => {
    const unsub = store.subscribe(() => {
      const state = store.getState().auth;
      localStorage.setItem(
        "aihc-auth",
        JSON.stringify({
          accessToken: state.accessToken,
          refreshToken: state.refreshToken,
          roles: state.roles,
          email: state.email,
          darkMode: state.darkMode,
        })
      );
      document.documentElement.classList.toggle("dark", state.darkMode);
    });
    return unsub;
  }, []);

  return <>{children}</>;
}

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <Provider store={store}>
      <ThemeSync>{children}</ThemeSync>
    </Provider>
  );
}
