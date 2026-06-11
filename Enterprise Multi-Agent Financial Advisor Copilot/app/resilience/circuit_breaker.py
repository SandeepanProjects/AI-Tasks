import time


class CircuitBreaker:

    def __init__(self, threshold=5):

        self.threshold = threshold

        self.failures = 0

        self.last_failure = 0


    def allow_request(self):

        if self.failures >= self.threshold:

            if time.time() - self.last_failure < 60:

                return False

            self.failures = 0

        return True


    def record_failure(self):

        self.failures += 1

        self.last_failure = time.time()