"""n8n workflow catalog and trigger API."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from auth.deps import CurrentUser
from workflows.catalog import N8N_WORKFLOWS, WORKFLOW_BY_ID
from workflows.triggers import trigger_n8n_workflow

router = APIRouter()


class WorkflowTriggerRequest(BaseModel):
    workflow_id: str = Field(..., description="Catalog workflow id")
    payload: Optional[Dict[str, Any]] = None


@router.get("/workflows")
async def list_workflows(user: CurrentUser):
    return {
        "engine": "n8n",
        "import_path": "n8n/workflows",
        "workflows": N8N_WORKFLOWS,
    }


@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str, user: CurrentUser):
    spec = WORKFLOW_BY_ID.get(workflow_id)
    if not spec:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return spec


@router.post("/workflows/trigger")
async def trigger_workflow(data: WorkflowTriggerRequest, user: CurrentUser):
    if data.workflow_id not in WORKFLOW_BY_ID:
        raise HTTPException(status_code=404, detail="Workflow not found")
    result = await trigger_n8n_workflow(data.workflow_id, data.payload or {})
    return result
