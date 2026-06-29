"""Async SQLAlchemy engine and session factory.

The same models work on SQLite (local dev) and MySQL (production) thanks to
SQLAlchemy's dialect abstraction — only the connection URL changes.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    pass


# Fly's internal Postgres proxy speaks plain TCP (no TLS), so disable SSL for
# the asyncpg driver — otherwise the TLS handshake is reset by the server.
_connect_args: dict = {}
if settings.database_url.startswith("postgresql+asyncpg"):
    _connect_args["ssl"] = False

engine = create_async_engine(
    settings.database_url, echo=False, pool_pre_ping=True, connect_args=_connect_args
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_models() -> None:
    """Create tables if they do not exist yet."""
    # Import models so they register on Base.metadata before create_all.
    from app.database import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
