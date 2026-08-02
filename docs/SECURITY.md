# Dashboards & Security

## Patient Dashboard

- Health summary
- Appointments
- Prescriptions
- Reports
- AI Chat
- Medication reminders

UI: `/dashboard` (patient role) · `/portal/patient`

## Doctor Dashboard

- Patient queue
- AI summaries
- Risk alerts
- Lab insights
- Clinical notes

UI: `/dashboard` (doctor role) · `/portal/doctor`

## Admin Dashboard

- Hospital analytics
- AI usage
- Appointment statistics
- Operational metrics

UI: `/dashboard` (admin role) · `/portal/admin`

API: `GET /api/v1/dashboard`

## Security

| Capability | Implementation |
|---|---|
| JWT Authentication | `auth/security.py`, `/login` `/register` |
| RBAC | `auth/deps.require_roles`, role claims in JWT |
| Audit logging | `audit_log` table + `AuditService` |
| Data encryption (AES-256) | `security/encryption.py` (Fernet, SHA-256 derived 256-bit key) |
| TLS/HTTPS | Terminate at reverse proxy (`docker/nginx.conf`); local HTTP for dev |
| Secrets management | Env / `.env` via `security/secrets.py` (Vault-ready) |
| HIPAA/GDPR-aware handling | Consent + PHI masking + audit trails |
| Consent management | `consents` table · `GET/POST /api/v1/consent` |
| PHI masking in AI prompts | `security/phi.py` applied in `generate_text()` |

### Security APIs

| Method | Path |
|---|---|
| GET | `/api/v1/security` |
| GET | `/api/v1/consent` |
| POST | `/api/v1/consent` |
| POST | `/api/v1/security/mask-phi` |
| GET | `/api/v1/security/audit` (admin) |

### Env

```env
SECRET_KEY=...
ENCRYPTION_KEY=...   # optional dedicated AES key material
PHI_MASKING_ENABLED=true
TLS_ENABLED=false    # true behind HTTPS proxy
```
