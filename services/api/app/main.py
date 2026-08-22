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

logger = get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="Professional core backend for LedgerOS",
        debug=settings.DEBUG,
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
    async def root() -> dict[str, str]:
        return {
            "message": "Ledger OS API is operational",
            "environment": settings.ENVIRONMENT,
        }

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "healthy"}

    app.include_router(
        api_router,
        prefix=settings.API_PREFIX,
    )

    return app


app = create_app()
