from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.seed import seed_db


async def init_db(db_session: AsyncSession) -> None:
    await seed_db(db_session)
