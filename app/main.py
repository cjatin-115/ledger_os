from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title="Ledger OS API",
    version="0.1.0",
    description="Core backend API service",
)

app.include_router(
    api_router,
    prefix="/api",
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