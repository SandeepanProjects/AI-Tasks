import re
from dataclasses import dataclass
from app.core.config import settings

@dataclass(frozen=True)
class GuardrailResult:
    allowed: bool
    text: str
    reason: str | None = None

class InputGuardrail:
    def validate(self, text: str) -> GuardrailResult:
        if len(text) > settings.max_input_chars:
            return GuardrailResult(False, "", "Input exceeds maximum length")

        patterns = [
            r"ignore\s+(all\s+)?previous\s+instructions",
            r"reveal\s+(the\s+)?system\s+prompt",
            r"developer\s+message",
        ]
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            return GuardrailResult(False, "", "Potential prompt injection detected")

        return GuardrailResult(True, text.strip())

class OutputGuardrail:
    def validate(self, text: str) -> GuardrailResult:
        if not text.strip():
            return GuardrailResult(False, "", "Empty model response")

        forbidden = ("SYSTEM_SECRET", "INTERNAL_TOOL_TOKEN")
        if any(x in text for x in forbidden):
            return GuardrailResult(False, "", "Sensitive internal content detected")

        return GuardrailResult(True, text.strip())
