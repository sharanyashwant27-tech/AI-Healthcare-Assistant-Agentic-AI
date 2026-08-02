"""Vector database introspection API."""

from fastapi import APIRouter

from auth.deps import CurrentUser
from vectordb.factory import describe_vector_db

router = APIRouter()


@router.get("/vector-db")
async def vector_db_info(user: CurrentUser):
    return describe_vector_db()
