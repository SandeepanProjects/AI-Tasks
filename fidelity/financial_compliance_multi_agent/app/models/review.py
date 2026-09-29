from datetime import datetime
from sqlalchemy import String, Text, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
class Review(Base):
    __tablename__="reviews"
    id: Mapped[str]=mapped_column(String(36),primary_key=True)
    tenant_id: Mapped[str]=mapped_column(String(100),index=True)
    submitted_by: Mapped[str]=mapped_column(String(200))
    content: Mapped[str]=mapped_column(Text)
    status: Mapped[str]=mapped_column(String(40),default="queued",index=True)
    result: Mapped[dict|None]=mapped_column(JSON,nullable=True)
    decision_comment: Mapped[str|None]=mapped_column(Text,nullable=True)
    decided_by: Mapped[str|None]=mapped_column(String(200),nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
