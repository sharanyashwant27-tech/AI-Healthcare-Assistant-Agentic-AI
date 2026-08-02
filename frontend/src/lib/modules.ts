export type AppModule = {
  id: string;
  name: string;
  href: string;
  description: string;
  roles: Array<"patient" | "doctor" | "admin" | "receptionist" | "all">;
};

export const APP_MODULES: AppModule[] = [
  {
    id: "patient-portal",
    name: "Patient Portal",
    href: "/portal/patient",
    description: "Personal health profile, history, and care actions.",
    roles: ["patient", "all"],
  },
  {
    id: "doctor-portal",
    name: "Doctor Portal",
    href: "/portal/doctor",
    description: "Clinician workspace for patients and appointments.",
    roles: ["doctor", "admin", "all"],
  },
  {
    id: "hospital-admin",
    name: "Hospital Admin",
    href: "/portal/admin",
    description: "Hospital operations, users, and system oversight.",
    roles: ["admin", "receptionist", "all"],
  },
  {
    id: "knowledge",
    name: "Medical Knowledge Assistant",
    href: "/knowledge",
    description: "WHO/CDC/SOP grounded answers with GraphRAG.",
    roles: ["all"],
  },
  {
    id: "appointments",
    name: "Appointment System",
    href: "/appointments",
    description: "Book, track, and manage clinical appointments.",
    roles: ["all"],
  },
  {
    id: "prescriptions",
    name: "Prescription Analyzer",
    href: "/prescriptions",
    description: "OCR extraction, interactions, and allergy checks.",
    roles: ["all"],
  },
  {
    id: "imaging",
    name: "Medical Image Assistant",
    href: "/imaging",
    description: "Assistive imaging review — not a radiology report.",
    roles: ["all"],
  },
  {
    id: "symptoms",
    name: "Symptom Checker",
    href: "/symptoms",
    description: "Uncertainty-aware symptom triage support.",
    roles: ["all"],
  },
  {
    id: "labs",
    name: "Lab Report Analyzer",
    href: "/labs",
    description: "CBC/liver/kidney/glucose summary and flags.",
    roles: ["all"],
  },
  {
    id: "chat",
    name: "Medical Chatbot",
    href: "/chat",
    description: "Master agent chatbot with specialist delegation.",
    roles: ["all"],
  },
  {
    id: "reminders",
    name: "Medication Reminder",
    href: "/reminders",
    description: "Schedule medicine reminders and alerts.",
    roles: ["patient", "all"],
  },
  {
    id: "insurance",
    name: "Insurance Assistant",
    href: "/insurance",
    description: "Coverage and claim eligibility estimates.",
    roles: ["all"],
  },
  {
    id: "emergency",
    name: "Emergency Assistant",
    href: "/emergency",
    description: "Red-flag detection and escalation guidance.",
    roles: ["all"],
  },
  {
    id: "follow-up",
    name: "Follow-up Agent",
    href: "/follow-up",
    description: "Schedule follow-ups, tests, and care notifications.",
    roles: ["all"],
  },
  {
    id: "telemedicine",
    name: "Telemedicine",
    href: "/telemedicine",
    description: "Virtual consultation rooms with clinicians.",
    roles: ["all"],
  },
  {
    id: "dashboard",
    name: "Health Dashboard",
    href: "/dashboard",
    description: "Role-aware health and operations overview.",
    roles: ["all"],
  },
  {
    id: "notifications",
    name: "Notification Center",
    href: "/notifications",
    description: "Reminders, alerts, and care notifications.",
    roles: ["all"],
  },
  {
    id: "nutrition",
    name: "Nutrition Assistant",
    href: "/nutrition",
    description: "BMI, calories, hydration, diet and exercise plans.",
    roles: ["all"],
  },
  {
    id: "workflows",
    name: "n8n Workflows",
    href: "/workflows",
    description: "Registration, appointments, emergency, prescription, and lab pipelines.",
    roles: ["admin", "doctor", "all"],
  },
];
