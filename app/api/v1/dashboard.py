from fastapi import APIRouter

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("")
async def get_dashboard() -> dict[str, int]:
    return {
        "suppliers": 0,
        "bills": 0,
        "payments": 0,
    }