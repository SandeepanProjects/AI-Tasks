from datetime import datetime
from sqlalchemy import String, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
class AuditEvent(Base):
    __tablename__="audit_events"
    id: Mapped[int]=mapped_column(primary_key=True)
    tenant_id: Mapped[str]=mapped_column(String(100),index=True)
    review_id: Mapped[str|None]=mapped_column(String(36),index=True,nullable=True)
    actor: Mapped[str]=mapped_column(String(200))
    action: Mapped[str]=mapped_column(String(100))
    details: Mapped[dict]=mapped_column(JSON,default=dict)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
