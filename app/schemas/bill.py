from pydantic import BaseModel


class BillCreate(BaseModel):
    supplier_id: int
    bill_number: str
    total_amount: float
    status: str = "pending"


class BillRead(BillCreate):
    id: int
