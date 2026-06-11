from prometheus_client import Counter, Histogram


REQUEST_COUNT = Counter(
    "rag_requests_total",
    "Total RAG requests"
)

REQUEST_LATENCY = Histogram(
    "rag_latency_seconds",
    "RAG latency"
)