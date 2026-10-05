from prometheus_client import Counter, Histogram

REQUESTS = Counter("api_requests_total", "API requests", ["route", "method", "status"])
REVIEW_JOBS = Counter("review_jobs_total", "Review jobs", ["status"])
REVIEW_LATENCY = Histogram("review_workflow_seconds", "Review workflow duration")
LLM_CALLS = Counter("llm_calls_total", "LLM calls", ["model", "status"])
