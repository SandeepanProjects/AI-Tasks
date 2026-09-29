# Interview narrative (adapt to what is actually implemented)

I designed an evidence-grounded market research platform with a FastAPI control plane, PostgreSQL as the system of record, pgvector for semantic retrieval, Redis/Celery for asynchronous ingestion, and LangGraph for bounded research orchestration. I used hexagonal architecture so model, database, and data-provider adapters can be replaced without changing use cases.

The main safety boundary is that the model produces a draft, not an executable investment action. The platform requires provenance-bearing evidence, validates structured output and citations, discloses limitations, and routes the report through a role-protected human review. Tenant identity comes from verified claims and is enforced in application queries plus PostgreSQL RLS.

For scale, I would make review creation idempotent, persist workflow checkpoints, use an outbox for reliable task dispatch, separate ingestion and inference queues, and measure p95 latency, provider freshness, retrieval quality, cost per report, review turnaround, and guardrail rejection rates. The included project is a reference scaffold; be precise about which adapters and integrations are wired in your deployment.
