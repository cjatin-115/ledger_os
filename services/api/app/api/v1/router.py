from fastapi import APIRouter

from app.api.v1 import (
    auth,
    admin,
    attachments,
    bill_scan,
    bills,
    dashboard,
    health,
    ledger,
    reminders,
    subscriptions,
    ocr_feedback,
    payments,
    payment_scan,
    suppliers,
)

api_router = APIRouter(
    prefix="/v1",
)

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(attachments.router)
api_router.include_router(suppliers.router)
api_router.include_router(bills.router)
api_router.include_router(bill_scan.router)
api_router.include_router(payment_scan.router)
api_router.include_router(payments.router)
api_router.include_router(dashboard.router)
api_router.include_router(ledger.router)
api_router.include_router(reminders.router)
api_router.include_router(subscriptions.router)
api_router.include_router(ocr_feedback.router)