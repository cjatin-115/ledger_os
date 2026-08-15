from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_suppliers() -> list[dict]:
    return []
