from fastapi import APIRouter

router = APIRouter(
    prefix="/bills",
    tags=["Bills"],
)


@router.get("")
async def list_bills() -> list[dict]:
    return []