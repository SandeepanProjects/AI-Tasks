from starlette.middleware.base import (
    BaseHTTPMiddleware
)

from app.monitoring.metrics import (
    REQUEST_COUNT
)


class MetricsMiddleware(
    BaseHTTPMiddleware
):

    async def dispatch(
        self,
        request,
        call_next
    ):

        REQUEST_COUNT.inc()

        return await call_next(
            request
        )