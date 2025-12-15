"""
Database Configuration

Sets up SQLAlchemy engine and session.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Use SQLite for local development if DATABASE_URL is not set
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL", "sqlite+aiosqlite:///./app.db")

# Synchronous Engine (for migrations/scripts)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Asynchronous Engine (for FastAPI)
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in ASYNC_DATABASE_URL else {}
)
AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """Dependency for getting async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
