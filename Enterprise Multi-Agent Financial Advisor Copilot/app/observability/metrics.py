from prometheus_client import (
    Counter,
    Histogram
)

AI_REQUESTS = Counter(
    "ai_requests_total",
    "Total AI Requests"
)

AI_LATENCY = Histogram(
    "ai_latency_seconds",
    "AI Request Latency"
)

RAG_RETRIEVALS = Counter(
    "rag_retrieval_total",
    "RAG Retrieval Count"
)

LLM_TOKENS = Counter(
    "llm_token_usage",
    "Token Usage"
)
REQUEST_COUNT = Counter(
    "rag_requests_total",
    "Total RAG requests"
)

REQUEST_LATENCY = Histogram(
    "rag_latency_seconds",
    "RAG latency"
)


#  pip install prometheus-client