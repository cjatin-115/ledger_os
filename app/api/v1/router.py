from fastapi import APIRouter

from app.api.v1 import auth, bills, dashboard, health, payments, suppliers

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(suppliers.router)
api_router.include_router(bills.router)
api_router.include_router(payments.router)
api_router.include_router(dashboard.router)