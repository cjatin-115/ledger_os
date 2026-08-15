from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_payments() -> list[dict]:
    return []
