# Architecture

- `api/routes`: HTTP boundaries, validation, response codes.
- `auth`: demo identity and role authorization (replace before production).
- `services`: lifecycle, state transitions, audit events.
- `agents`: independent reasoning roles: claim extraction, research, analysis, risk.
- `tools`: narrow, tenant-scoped capabilities called by workflow/agents.
- `graph`: LangGraph state and orchestration order.
- `rag`: policy ingestion, embeddings, retrieval.
- `models/db`: PostgreSQL persistence; pgvector stores embeddings.
- `cache`: Redis retrieval cache; tenant and query digest included in key.
- `worker`: Celery queue for long-running reviews.
- `guardrails`: schema validation and citation provenance checks.

Agent ≠ tool: agents perform a reasoning task; tools are bounded application functions. Tool execution remains application-controlled for authorization and validation. Review lifecycle: `queued → processing → pending_approval → approved|rejected`; failures become `failed`.

No API key means deterministic fallback analysis and keyword search. With a key, OpenAI JSON-mode responses and embeddings are used. Add robust retries/timeouts, prompt-injection defenses, PII handling, full OpenTelemetry, Alembic migrations, durable graph checkpointing, rate limits, security/load tests, and operational dashboards before production.
