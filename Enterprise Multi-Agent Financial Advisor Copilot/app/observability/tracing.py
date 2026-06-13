import time


class Tracer:

    @staticmethod
    def trace(func):

        def wrapper(*args, **kwargs):

            start = time.time()

            result = func(*args, **kwargs)

            end = time.time()

            print(
                f"[TRACE] {func.__name__} took {end - start}s"
            )

            return result

        return wrapper
    
    
#     pip install opentelemetry-api
# pip install opentelemetry-sdk

from functools import wraps

from opentelemetry import trace


tracer = trace.get_tracer(
    "financial-copilot"
)


def traced(span_name):

    def decorator(func):

        @wraps(func)

        async def wrapper(
            *args,
            **kwargs
        ):

            with tracer.start_as_current_span(
                span_name
            ):

                return await func(
                    *args,
                    **kwargs
                )

        return wrapper

    return decorator