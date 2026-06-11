import time
import uuid


class TraceMiddleware:

    def __init__(self, app):

        self.app = app


    async def __call__(self, request, call_next):

        trace_id = str(uuid.uuid4())

        start = time.time()

        response = await call_next(request)

        duration = time.time() - start

        print(
            f"[TRACE] {trace_id} "
            f"{request.url} "
            f"{duration}s"
        )

        response.headers["X-Trace-ID"] = trace_id

        return response