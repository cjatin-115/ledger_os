from pydantic import BaseModel


class PaymentCreate(BaseModel):
    bill_id: int | None = None
    payment_reference: str
    amount: float
    status: str = "pending"


class PaymentRead(PaymentCreate):
    id: int
