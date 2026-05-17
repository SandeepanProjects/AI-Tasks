import time
from prometheus_client import Counter, Histogram, Gauge

# Core metrics
REQUEST_COUNT = Counter(
    "rec_requests_total",
    "Total recommendation requests"
)

REQUEST_LATENCY = Histogram(
    "rec_request_latency_seconds",
    "Request latency distribution"
)

CACHE_HIT = Counter(
    "rec_cache_hit_total",
    "Cache hit count"
)

CACHE_MISS = Counter(
    "rec_cache_miss_total",
    "Cache miss count"
)

ACTIVE_USERS = Gauge(
    "rec_active_users",
    "Active users in system"
)


class MetricsTracker:

    def start_timer(self):
        return time.time()

    def observe_latency(self, start_time: float):
        REQUEST_LATENCY.observe(time.time() - start_time)

    def track_request(self):
        REQUEST_COUNT.inc()

    def track_cache(self, hit: bool):
        if hit:
            CACHE_HIT.inc()
        else:
            CACHE_MISS.inc()