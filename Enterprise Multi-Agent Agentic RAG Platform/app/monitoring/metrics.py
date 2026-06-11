from prometheus_client import Counter


REQUEST_COUNT = Counter(
    "request_count",
    "Total requests"
)

TOKEN_USAGE = Counter(
    "token_usage",
    "Token usage"
)