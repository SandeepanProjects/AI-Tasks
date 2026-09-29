import uuid
from app.db.models import AuditEvent

class AuditService:
    def __init__(self, db): self.db = db

    async def record(self, *, tenant_id: str, review_id: str, actor_id: str,
                     event_type: str, details: dict) -> None:
        self.db.add(AuditEvent(id=str(uuid.uuid4()), tenant_id=tenant_id,
            review_id=review_id, actor_id=actor_id, event_type=event_type, details=details))
        await self.db.flush()
