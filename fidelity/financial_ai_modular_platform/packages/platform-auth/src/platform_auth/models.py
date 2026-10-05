from dataclasses import dataclass, field

@dataclass(frozen=True)
class Principal:
    subject: str
    tenant_id: str
    roles: frozenset[str] = field(default_factory=frozenset)
