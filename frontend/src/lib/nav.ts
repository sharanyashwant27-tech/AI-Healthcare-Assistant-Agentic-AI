export const NAV_LINKS = [
  { href: "/modules", label: "Modules" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/portal/patient", label: "Patient Portal" },
  { href: "/portal/doctor", label: "Doctor Portal" },
  { href: "/portal/admin", label: "Admin Portal" },
  { href: "/chat", label: "Chatbot" },
  { href: "/symptoms", label: "Symptoms" },
  { href: "/appointments", label: "Appointments" },
  { href: "/telemedicine", label: "Telemedicine" },
  { href: "/knowledge", label: "Knowledge" },
  { href: "/prescriptions", label: "Prescriptions" },
  { href: "/imaging", label: "Imaging" },
  { href: "/labs", label: "Labs" },
  { href: "/nutrition", label: "Nutrition" },
  { href: "/reminders", label: "Reminders" },
  { href: "/follow-up", label: "Follow-up" },
  { href: "/insurance", label: "Insurance" },
  { href: "/emergency", label: "Emergency" },
  { href: "/workflows", label: "Workflows" },
  { href: "/notifications", label: "Notifications" },
] as const;

export type NavHref = (typeof NAV_LINKS)[number]["href"];

export const publicPaths = new Set(["/", "/login", "/register"]);

/** Map dashboard/stat card keys to destination pages + optional task hints. */
export const STAT_LINKS: Record<string, { href: string; label: string }> = {
  appointments: { href: "/appointments", label: "Appointments" },
  upcoming_appointments: { href: "/appointments", label: "Appointments" },
  prescriptions: { href: "/prescriptions", label: "Prescriptions" },
  reports: { href: "/labs", label: "Lab reports" },
  lab_reports: { href: "/labs", label: "Lab reports" },
  reminders: { href: "/reminders", label: "Reminders" },
  notifications: { href: "/notifications", label: "Notifications" },
  unread_notifications: { href: "/notifications", label: "Notifications" },
  patients: { href: "/portal/patient", label: "Patient portal" },
  doctors: { href: "/portal/doctor", label: "Doctor portal" },
  users: { href: "/modules", label: "Modules" },
  hospitals: { href: "/dashboard", label: "Dashboard" },
  emergencies: { href: "/emergency", label: "Emergency" },
  telemedicine: { href: "/telemedicine", label: "Telemedicine" },
  workflows: { href: "/workflows", label: "Workflows" },
  chat: { href: "/chat", label: "Chat" },
  symptoms: { href: "/symptoms", label: "Symptoms" },
  insurance: { href: "/insurance", label: "Insurance" },
  knowledge: { href: "/knowledge", label: "Knowledge" },
};
