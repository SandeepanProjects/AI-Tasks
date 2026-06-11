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