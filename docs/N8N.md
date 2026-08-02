# n8n Workflows

Import JSON files from `n8n/workflows` into n8n (UI → Workflows → Import). Docker Compose mounts that folder at `/workflows`.

Base webhook URL: `http://localhost:5678/webhook` (`N8N_WEBHOOK_URL`).

## Workflow 1 — Patient Registration

`patient-registration.json` · webhook `patient-registration`

```text
Form → Validate → Create Patient → Send Email → Send SMS → Store Database
```

Triggered after patient registration (`POST /api/v1/register`).

## Workflow 2 — Appointment

`appointment-booking.json` · webhook `appointment-booking`

```text
Book → Doctor Availability → Calendar → Confirmation → Reminder
```

Triggered after `POST /api/v1/appointment`.

## Workflow 3 — Emergency

`emergency-alert.json` · webhook `emergency-alert`

```text
Symptoms → Critical Check → Doctor Alert → Ambulance → Hospital → Family Notification
```

Triggered by the Emergency Agent on critical symptoms.

## Workflow 4 — Prescription

`prescription-ocr.json` · webhook `prescription-ocr`

```text
Upload → OCR → AI → Medicine Extraction → Interaction Check → Patient
```

Triggered after `POST /api/v1/prescription`.

## Workflow 5 — Lab Report

`lab-report-ocr.json` · webhook `lab-report-ocr`

```text
Upload → OCR → AI Analysis → Doctor → Patient Summary
```

Triggered after `POST /api/v1/lab-report`.

## Supporting workflows

Also included for channel reuse: `email-notification`, `sms-notification`, `push-notification`, `medicine-reminder`, `insurance-validation`.

## API

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/workflows` | Catalog of the five pipelines |
| `GET` | `/api/v1/workflows/{id}` | Single workflow |
| `POST` | `/api/v1/workflows/trigger` | Manually fire a webhook (`workflow_id` + `payload`) |

If n8n is offline, triggers return a soft fallback with `simulated_steps` and do not fail the primary API call.
