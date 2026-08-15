from pydantic import BaseModel


class SupplierCreate(BaseModel):
    name: str
    contact_person: str | None = None


class SupplierRead(SupplierCreate):
    id: int
