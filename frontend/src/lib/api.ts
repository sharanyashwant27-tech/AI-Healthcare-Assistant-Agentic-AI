// Prefer 127.0.0.1 over "localhost" — browsers often resolve localhost to ::1,
// while the API may only listen on IPv4 (login then fails with "Failed to fetch").
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

export type TokenBundle = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  roles: string[];
};

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null
): Promise<T> {
  const headers = new Headers(options.headers || {});
  if (!(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(typeof err.detail === "string" ? err.detail : JSON.stringify(err.detail) || "Request failed");
  }
  return res.json();
}

export const api = {
  login: (email: string, password: string) =>
    request<TokenBundle>("/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  register: (payload: Record<string, unknown>) =>
    request("/register", { method: "POST", body: JSON.stringify(payload) }),
  me: (token: string) => request("/me", {}, token),
  dashboard: (token: string) => request<any>("/dashboard", {}, token),
  security: (token: string) => request<any>("/security", {}, token),
  consents: (token: string) => request<any>("/consent", {}, token),
  updateConsent: (token: string, payload: Record<string, unknown>) =>
    request("/consent", { method: "POST", body: JSON.stringify(payload) }, token),
  chat: (token: string, message: string, conversation_id?: string, extras?: Record<string, unknown>) =>
    request<any>(
      "/chat",
      {
        method: "POST",
        body: JSON.stringify({ message, conversation_id, ...(extras || {}) }),
      },
      token
    ),
  advancedAi: (token: string) => request<any>("/advanced-ai", {}, token),
  hitlReviews: (token: string) => request<any[]>("/hitl/reviews", {}, token),
  hitlDecide: (token: string, reviewId: string, payload: Record<string, unknown>) =>
    request(`/hitl/reviews/${reviewId}/decision`, {
      method: "POST",
      body: JSON.stringify(payload),
    }, token),
  runEval: (token: string) => request<any>("/eval/run", { method: "POST" }, token),
  fhirMetadata: (token: string) => request<any>("/fhir/metadata", {}, token),
  symptomAnalysis: (token: string, payload: Record<string, unknown>) =>
    request("/symptom-analysis", { method: "POST", body: JSON.stringify(payload) }, token),
  doctors: (token: string) => request<any[]>("/doctor", {}, token),
  patients: (token: string) => request<any[]>("/patient", {}, token),
  appointments: (token: string) => request<any[]>("/appointment", {}, token),
  createAppointment: (token: string, payload: Record<string, unknown>) =>
    request("/appointment", { method: "POST", body: JSON.stringify(payload) }, token),
  nutrition: (token: string, payload: Record<string, unknown>) =>
    request("/nutrition", { method: "POST", body: JSON.stringify(payload) }, token),
  insurance: (token: string, payload: Record<string, unknown>) =>
    request("/insurance", { method: "POST", body: JSON.stringify(payload) }, token),
  emergency: (token: string, payload: Record<string, unknown>) =>
    request("/emergency", { method: "POST", body: JSON.stringify(payload) }, token),
  knowledge: (token: string, query: string, use_graph = true) =>
    request("/knowledge", { method: "POST", body: JSON.stringify({ query, use_graph }) }, token),
  embeddings: (token: string) => request<any>("/embeddings", {}, token),
  vectorDb: (token: string) => request<any>("/vector-db", {}, token),
  prompts: (token: string) => request<any>("/prompts", {}, token),
  workflows: (token: string) => request<any>("/workflows", {}, token),
  triggerWorkflow: (token: string, workflow_id: string, payload?: Record<string, unknown>) =>
    request("/workflows/trigger", {
      method: "POST",
      body: JSON.stringify({ workflow_id, payload }),
    }, token),
  followUp: (token: string, payload: Record<string, unknown>) =>
    request("/follow-up", { method: "POST", body: JSON.stringify(payload) }, token),
  createReminder: (token: string, payload: Record<string, unknown>) =>
    request("/reminder", { method: "POST", body: JSON.stringify(payload) }, token),
  reminders: (token: string) => request<any[]>("/reminder", {}, token),
  startTelemedicine: (token: string, payload: Record<string, unknown>) =>
    request("/telemedicine", { method: "POST", body: JSON.stringify(payload) }, token),
  telemedicineSessions: (token: string) => request<any[]>("/telemedicine", {}, token),
  notifications: (token: string) => request<any[]>("/notifications", {}, token),
  markNotificationRead: (token: string, id: number) =>
    request(`/notifications/${id}/read`, { method: "POST" }, token),
  markAllNotificationsRead: (token: string) =>
    request("/notifications/read-all", { method: "POST" }, token),
  prescriptionText: async (token: string, text: string, allergies?: string) => {
    const form = new FormData();
    form.append("text", text);
    if (allergies) form.append("allergies", allergies);
    return request("/prescription", { method: "POST", body: form }, token);
  },
  labText: async (token: string, text: string) => {
    const form = new FormData();
    form.append("text", text);
    return request("/lab-report", { method: "POST", body: form }, token);
  },
  medicalImage: async (token: string, file: File | null, modality: string, notes: string) => {
    const form = new FormData();
    form.append("modality", modality);
    form.append("notes", notes);
    if (file) form.append("file", file);
    return request("/medical-image", { method: "POST", body: form }, token);
  },
};
