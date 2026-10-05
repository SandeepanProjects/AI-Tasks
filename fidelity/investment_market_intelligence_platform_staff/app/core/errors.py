class DomainError(Exception):
    code = "domain_error"
    status_code = 422
    def __init__(self, message: str): super().__init__(message)

class NotFoundError(DomainError):
    code, status_code = "not_found", 404

class AuthorizationError(DomainError):
    code, status_code = "forbidden", 403

class ConflictError(DomainError):
    code, status_code = "conflict", 409

class GuardrailViolation(DomainError):
    code, status_code = "guardrail_violation", 422

class InfrastructureError(DomainError):
    code, status_code = "infrastructure_error", 503
