"""Workflow helpers for n8n webhook integration."""

from core.config import settings
from workflows.catalog import N8N_WORKFLOWS, WORKFLOW_BY_ID
from workflows.triggers import trigger_n8n_workflow


def n8n_webhook(path: str) -> str:
    return f"{settings.n8n_webhook_url.rstrip('/')}/{path.lstrip('/')}"


__all__ = [
    "N8N_WORKFLOWS",
    "WORKFLOW_BY_ID",
    "n8n_webhook",
    "trigger_n8n_workflow",
]
