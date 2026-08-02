# Database Tables

Canonical healthcare tables (SQLAlchemy models in `backend/models/`):

| Entity | Table | Model |
|---|---|---|
| Patients | `patients` | `Patient` |
| Doctors | `doctors` | `Doctor` |
| Appointments | `appointments` | `Appointment` |
| Medicines | `medicines` | `Medicine` |
| Prescriptions | `prescriptions` | `Prescription` |
| Diseases | `diseases` | `Disease` |
| Symptoms | `symptoms` | `Symptom` |
| LabReports | `lab_reports` | `LabReport` |
| Insurance | `insurance` | `Insurance` |
| Hospitals | `hospitals` | `Hospital` |
| Notifications | `notifications` | `Notification` |
| MedicalHistory | `medical_history` | `MedicalHistory` |

Supporting tables: `users`, `roles`, `user_roles`, `audit_log`.

## Relationships

```text
Hospital ──< Doctor ──< Appointment >── Patient
                              │
Patient ──< Prescription
Patient ──< LabReport >── Doctor / Hospital
Patient ──< Insurance
Patient ──< MedicalHistory
User ──< Notification
```

## API

`GET /api/v1/database/tables` — catalog + existing DB table names

## Notes

- Local default: SQLite (`USE_SQLITE=true`)
- Compose: PostgreSQL (`USE_SQLITE=false`)
- `init_db()` creates missing tables; SQLite also ensures new FK columns via `database/migrate.py`
