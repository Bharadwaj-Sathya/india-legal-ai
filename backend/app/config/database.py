import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

from config.configuration import Configuration

# -------------------------------------------------
# Logging
# -------------------------------------------------
logger = logging.getLogger(__name__)

# -------------------------------------------------
# Load configuration
# -------------------------------------------------
config = Configuration.load()

# -------------------------------------------------
# Create async engine
# -------------------------------------------------
engine = create_async_engine(
    config.DATABASE_URL,
    echo=False, # config.DEBUG,  # SQL logs only in debug
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # auto-recover stale connections
)

# -------------------------------------------------
# Session factory
# -------------------------------------------------
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# -------------------------------------------------
# Dependency: DB session
# -------------------------------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # Automatically commit if no exceptions occurred
            await session.commit()
        except Exception as e:
            # Rollback on any exception
            await session.rollback()
            logger.exception("Database session error")
            raise
        finally:
            await session.close()
