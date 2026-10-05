from contextvars import ContextVar
from uuid import uuid4

correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")

def new_correlation_id() -> str:
    value = str(uuid4())
    correlation_id.set(value)
    return value
