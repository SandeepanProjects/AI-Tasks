from collections.abc import Callable
from .models import GuardrailResult

class GuardrailEngine:
    def __init__(self, validators: list[Callable[[str], list[str]]]):
        self.validators = validators

    def check(self, text: str) -> GuardrailResult:
        reasons = []
        for validator in self.validators:
            reasons.extend(validator(text))
        return GuardrailResult(allowed=not reasons, reasons=reasons)
