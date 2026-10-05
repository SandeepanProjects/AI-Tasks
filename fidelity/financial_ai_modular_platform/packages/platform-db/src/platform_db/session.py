from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

class Database:
    """Generic DB mechanics. Business repositories belong to applications."""

    def __init__(self, dsn: str):
        self.engine: AsyncEngine = create_async_engine(dsn, pool_pre_ping=True)
        self.sessions = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    def session(self) -> AsyncSession:
        return self.sessions()
