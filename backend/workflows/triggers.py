"""Fire-and-forget n8n webhook triggers."""

from typing import Any, Dict, Optional

import httpx

from core.config import settings
from core.logging import get_logger
from workflows.catalog import WORKFLOW_BY_ID

logger = get_logger(__name__)


def _webhook_url(path: str) -> str:
    return f"{settings.n8n_webhook_url.rstrip('/')}/{path.lstrip('/')}"


async def trigger_n8n_workflow(
    workflow_id: str,
    payload: Optional[Dict[str, Any]] = None,
    timeout: float = 5.0,
) -> Dict[str, Any]:
    """POST to the n8n webhook for a catalog workflow. Never raises to callers."""
    spec = WORKFLOW_BY_ID.get(workflow_id)
    if not spec:
        return {"triggered": False, "error": f"unknown workflow: {workflow_id}"}

    url = _webhook_url(spec["webhook_path"])
    body = {"workflow_id": workflow_id, "steps": spec["steps"], **(payload or {})}

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, json=body)
        logger.info(
            "n8n_workflow_triggered",
            workflow_id=workflow_id,
            status_code=resp.status_code,
            url=url,
        )
        return {
            "triggered": True,
            "workflow_id": workflow_id,
            "webhook_path": spec["webhook_path"],
            "status_code": resp.status_code,
            "url": url,
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "n8n_workflow_unavailable",
            workflow_id=workflow_id,
            url=url,
            error=str(exc),
            n8n_base=settings.n8n_webhook_url,
        )
        return {
            "triggered": False,
            "workflow_id": workflow_id,
            "webhook_path": spec["webhook_path"],
            "fallback": True,
            "error": str(exc),
            "simulated_steps": spec["steps"],
        }
