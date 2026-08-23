from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import (
    ConflictError,
    LedgerOSError,
    NotFoundError,
    ValidationError,
)
from app.core.logging import get_logger
from app.db import models  # noqa: F401
from app.db.base import Base
from app.db.seed import seed_development_data
from app.db.session import AsyncSessionLocal, engine

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables verified.")
    except Exception as exc:
        logger.warning(f"Database schema check skipped/failed: {exc}")

    try:
        async with AsyncSessionLocal() as session:
            await seed_development_data(session)
        logger.info("Seed data verified.")
    except Exception as exc:
        logger.warning(f"Database seed data check skipped/failed: {exc}")

    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="Professional core backend for LedgerOS",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(LedgerOSError)
    async def ledger_os_exception_handler(request: Request, exc: LedgerOSError):
        status_code = 500
        if isinstance(exc, NotFoundError):
            status_code = 404
        elif isinstance(exc, ValidationError):
            status_code = 422
        elif isinstance(exc, ConflictError):
            status_code = 409

        logger.warning(
            "LedgerOS error handled",
            extra={
                "path": request.url.path,
                "method": request.method,
                "error_type": type(exc).__name__,
                "message": str(exc),
            },
        )

        return JSONResponse(
            status_code=status_code,
            content={
                "detail": str(exc),
                "error": type(exc).__name__,
                "details": exc.details,
            },
        )

    @app.get("/")
    @app.head("/", include_in_schema=False)
    async def root() -> dict[str, str]:
        return {
            "message": "Ledger OS API is operational",
            "environment": settings.ENVIRONMENT,
        }

    @app.get("/health")
    @app.head("/health", include_in_schema=False)
    async def health_check() -> dict[str, str]:
        return {"status": "healthy"}

    app.include_router(
        api_router,
        prefix=settings.API_PREFIX,
    )

    return app


app = create_app()
