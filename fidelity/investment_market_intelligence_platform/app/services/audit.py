from datetime import datetime, timezone
from dataclasses import dataclass

@dataclass(frozen=True)
class AuditEvent:
    tenant_id: str
    actor_id: str
    action: str
    resource_id: str
    occurred_at: datetime
    details: dict

def make_audit_event(tenant_id: str, actor_id: str, action: str, resource_id: str, **details):
    # Production: persist append-only, restrict UPDATE/DELETE, ship to SIEM/WORM storage.
    return AuditEvent(tenant_id, actor_id, action, resource_id, datetime.now(timezone.utc), details)
