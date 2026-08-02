"""API catalog endpoint."""

from fastapi import APIRouter

from api.catalog import CORE_APIS
from core.config import settings

router = APIRouter()


@router.get("/apis")
async def list_core_apis():
    prefix = settings.api_prefix.rstrip("/")
    return {
        "base_url": f"http://localhost:{settings.backend_port}{prefix}",
        "prefix": prefix,
        "apis": [
            {
                **item,
                "full_path": f"{prefix}{item['path']}",
            }
            for item in CORE_APIS
        ],
    }
