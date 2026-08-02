"""Prompt engineering catalog API."""

from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from auth.deps import CurrentUser
from prompts.builder import build_prompt, describe_prompt_engineering

router = APIRouter()


class PromptPreviewRequest(BaseModel):
    name: str = Field(..., description="Template name, e.g. symptom | prescription")
    variables: Dict[str, Any] = Field(default_factory=dict)
    dynamic: Optional[Dict[str, Any]] = None
    include_few_shot: bool = False


@router.get("/prompts")
async def prompts_catalog(user: CurrentUser):
    return describe_prompt_engineering()


@router.post("/prompts/preview")
async def prompts_preview(data: PromptPreviewRequest, user: CurrentUser):
    rendered = build_prompt(
        data.name,
        data.variables,
        dynamic_payload=data.dynamic,
        include_few_shot=data.include_few_shot,
    )
    return {"name": data.name, "rendered": rendered}
