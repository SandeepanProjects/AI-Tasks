from dataclasses import dataclass, field

@dataclass(frozen=True)
class GuardrailResult:
    allowed: bool
    reasons: list[str] = field(default_factory=list)
    transformed_text: str | None = None
