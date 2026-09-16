"""
Database Module - SQLAlchemy 2.0 Async Engine and Session Management.

Why this exists:
1. SQLAlchemy 2.0 Async Architecture:
   Non-blocking asynchronous database queries via `asyncpg` ensure the FastAPI event loop
   remains unblocked under high concurrent traffic loads (e.g. streaming logs, active student quizzes).

2. Connection Pooling (`pool_pre_ping=True`):
   Detects stale or dropped connections (e.g. following database restarts or network timeouts)
   and automatically refreshes them before executing queries.

3. Dependency Injection (`get_db`):
   Provides request-scoped database sessions. FastAPI injects the session into route handlers,
   guaranteeing each request operates in its own transaction context and automatically
   rolls back if an unhandled exception occurs.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
from app.core.logging import logger

# Initialize Async Engine with robust pooling parameters
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,                     # Verifies connection liveness before checking out
    pool_size=settings.DB_POOL_SIZE,        # Base pool connection count
    max_overflow=settings.DB_MAX_OVERFLOW,  # Burst connection allowance
    pool_timeout=settings.DB_POOL_TIMEOUT,  # Max wait time for available connection
)

# Async Session Factory
# expire_on_commit=False prevents lazy-load attribute expiration after commits
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """
    Base declarative class for all SQLAlchemy 2.0 models.
    Provides metadata registry for Alembic migration autogeneration.
    """
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an asynchronous SQLAlchemy session per request.
    
    Guarantees:
    - Dedicated session per HTTP request
    - Automatic rollback on unhandled exceptions
    - Guaranteed cleanup/close on completion
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as exc:
            logger.error(f"Database session error encountered: {exc}", exc_info=True)
            await session.rollback()
            raise
        finally:
            await session.close()
