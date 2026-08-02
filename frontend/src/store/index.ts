import { configureStore, createSlice, PayloadAction } from "@reduxjs/toolkit";

type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  roles: string[];
  email: string | null;
  darkMode: boolean;
};

const initialState: AuthState = {
  accessToken: null,
  refreshToken: null,
  roles: [],
  email: null,
  darkMode: false,
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setAuth(
      state,
      action: PayloadAction<{
        accessToken: string;
        refreshToken: string;
        roles: string[];
        email: string;
      }>
    ) {
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken;
      state.roles = action.payload.roles;
      state.email = action.payload.email;
    },
    logout(state) {
      state.accessToken = null;
      state.refreshToken = null;
      state.roles = [];
      state.email = null;
    },
    toggleDarkMode(state) {
      state.darkMode = !state.darkMode;
    },
    hydrate(state, action: PayloadAction<Partial<AuthState>>) {
      Object.assign(state, action.payload);
    },
  },
});

export const { setAuth, logout, toggleDarkMode, hydrate } = authSlice.actions;

export const store = configureStore({
  reducer: { auth: authSlice.reducer },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
