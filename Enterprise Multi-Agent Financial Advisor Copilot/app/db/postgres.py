# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from app.core.config import settings


# DATABASE_URL = (
#     f"postgresql://"
#     f"{settings.POSTGRES_USER}:"
#     f"{settings.POSTGRES_PASSWORD}@"
#     f"{settings.POSTGRES_HOST}:"
#     f"{settings.POSTGRES_PORT}/"
#     f"{settings.POSTGRES_DB}"
# )

# engine = create_engine(
#     DATABASE_URL,
#     pool_pre_ping=True,
#     pool_size=20,
#     max_overflow=10
# )

# SessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine
# )


# def get_db():

#     db = SessionLocal()

#     try:
#         yield db

#     finally:
#         db.close()


# app/db/postgres.py

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from app.config.settings import settings


engine = create_async_engine(
    settings.DATABASE_URL,

    pool_size=20,

    max_overflow=40,

    pool_pre_ping=True,

    echo=False
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,

    expire_on_commit=False,

    autoflush=False,

    autocommit=False,

    class_=AsyncSession
)


async def get_db() -> AsyncGenerator:

    async with AsyncSessionLocal() as session:

        yield session