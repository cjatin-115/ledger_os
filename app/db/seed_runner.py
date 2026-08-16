import asyncio

from app.db.seed import seed_development_data
from app.db.session import AsyncSessionLocal


async def main() -> None:
    async with AsyncSessionLocal() as db:
        await seed_development_data(db)


if __name__ == "__main__":
    asyncio.run(main())