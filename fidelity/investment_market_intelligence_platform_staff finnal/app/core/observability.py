import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.core.logging import bind_request_context
from app.core.metrics import REQUESTS

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        supplied_id = request.headers.get("X-Correlation-ID", "")
        safe_id = supplied_id if (1 <= len(supplied_id) <= 128 and all(c.isalnum() or c in "-_." for c in supplied_id)) else ""
        correlation_id = safe_id or str(uuid.uuid4())
        bind_request_context(correlation_id=correlation_id)
        try:
            response = await call_next(request)
        finally:
            from structlog.contextvars import clear_contextvars
            clear_contextvars()
        response.headers["X-Correlation-ID"] = correlation_id
        route = request.scope.get("route")
        route_label = getattr(route, "path", "unmatched")
        REQUESTS.labels(route_label, request.method, str(response.status_code)).inc()
        return response
