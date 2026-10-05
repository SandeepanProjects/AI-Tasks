class AppError(Exception):
    """Base application error."""


class ValidationError(AppError):
    """Input or state validation failed."""


class AuthorizationError(AppError):
    """Caller is not authorized."""


class NotFoundError(AppError):
    """Requested resource does not exist."""
