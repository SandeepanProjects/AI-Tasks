import json
import time


class RequestLogger:

    async def __call__(self, request, call_next):

        start = time.time()

        response = await call_next(request)

        log = {

            "path": str(request.url),

            "method": request.method,

            "duration": time.time() - start
        }

        print(json.dumps(log))

        return response