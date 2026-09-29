from datetime import datetime
from sqlalchemy import String, Text, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.db.base import Base
from app.core.config import settings
class PolicyChunk(Base):
    __tablename__="policy_chunks"
    id: Mapped[int]=mapped_column(primary_key=True)
    tenant_id: Mapped[str]=mapped_column(String(100),index=True)
    policy_code: Mapped[str]=mapped_column(String(100),index=True)
    title: Mapped[str]=mapped_column(String(300))
    text: Mapped[str]=mapped_column(Text)
    embedding: Mapped[list|None]=mapped_column(Vector(settings.embedding_dimensions),nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
    __table_args__=(Index("ix_policy_tenant_code","tenant_id","policy_code"),)
