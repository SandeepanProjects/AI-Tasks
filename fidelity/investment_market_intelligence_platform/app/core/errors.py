class DomainError(Exception):
    code = "domain_error"
    def __init__(self, message: str):
        super().__init__(message)

class NotFoundError(DomainError):
    code = "not_found"

class AuthorizationError(DomainError):
    code = "forbidden"

class GuardrailViolation(DomainError):
    code = "guardrail_violation"

class ConflictError(DomainError):
    code = "conflict"
