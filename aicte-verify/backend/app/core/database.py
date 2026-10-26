"""Database setup and session management for AICTE-Verify.

Uses SQLAlchemy 2.0 with asynchronous engine and session support.
Supports SQLite (aiosqlite) and PostgreSQL (asyncpg).
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


def get_async_database_url(url: str) -> str:
    """Normalize synchronous database URLs to their async driver equivalents."""
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


# Resolve async connection string
ASYNC_DATABASE_URL = get_async_database_url(settings.DATABASE_URL)

# Engine configuration
connect_args = {}
if "sqlite" in ASYNC_DATABASE_URL:
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    future=True,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy 2 models."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an asynchronous database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db(drop: bool = False) -> None:
    """Create all database tables using Base metadata, optionally dropping first."""
    async with engine.begin() as conn:
        if drop:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
