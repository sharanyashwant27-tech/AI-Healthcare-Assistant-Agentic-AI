"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from api.v1 import api_router
from api.v1.ws import router as ws_router
from core.config import settings
from database import AsyncSessionLocal, init_db
from core.logging import configure_logging, get_logger
from core.redis_client import close_redis
from middleware.rate_limit import RateLimitMiddleware
from schemas.common import HealthResponse
from utils.seed import seed_database

configure_logging()
logger = get_logger(__name__)
APP_VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_database(session)
        await session.commit()
    logger.info("application_started", env=settings.app_env, version=APP_VERSION)
    yield
    await close_redis()
    logger.info("application_stopped")


app = FastAPI(
    title=settings.app_name,
    version=APP_VERSION,
    description=(
        "Enterprise AI Healthcare Assistant with Agentic AI, RAG, GraphRAG, "
        "JWT RBAC, and multi-provider LLM support. "
        "Not a substitute for professional medical advice."
    ),
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list + ["http://localhost:8911", "http://127.0.0.1:8911"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)

app.include_router(api_router, prefix=settings.api_prefix)
app.include_router(ws_router)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    checks = {"database": "ok", "api": "ok"}
    try:
        from vectordb.factory import get_vector_service

        checks["vector_db"] = get_vector_service().health()
    except Exception as exc:  # noqa: BLE001
        checks["vector_db"] = f"error:{exc}"
    try:
        from graphrag.neo4j_client import get_graph_service

        checks["neo4j"] = get_graph_service().health()
    except Exception as exc:  # noqa: BLE001
        checks["neo4j"] = f"error:{exc}"
    try:
        from utils.storage import get_storage

        checks["storage"] = get_storage().health()
    except Exception as exc:  # noqa: BLE001
        checks["storage"] = f"error:{exc}"
    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        version=APP_VERSION,
        checks=checks,
    )


@app.get("/", tags=["Health"])
async def root():
    return {
        "name": settings.app_name,
        "version": APP_VERSION,
        "docs": "/docs",
        "frontend": f"http://localhost:{settings.frontend_port}",
        "disclaimer": settings.medical_disclaimer,
    }


if settings.prometheus_enabled:
    try:
        from prometheus_fastapi_instrumentator import Instrumentator

        Instrumentator().instrument(app).expose(app, endpoint="/metrics")
    except Exception as exc:  # noqa: BLE001
        logger.warning("prometheus_disabled", error=str(exc))
