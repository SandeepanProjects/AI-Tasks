# Architecture and design decisions

## Request path

1. FastAPI validates the request and resolves a Principal from local development JWT or OIDC/JWKS.
2. The application validates domain constraints.
3. One PostgreSQL transaction writes the review, tenant-scoped idempotency record, audit event, and outbox event.
4. The API returns `202 Accepted`. It makes a best-effort Celery dispatch; Celery Beat republishes uncompleted outbox events if the broker was unavailable or a worker died. Administrators can requeue terminal failures through a new transactional outbox event.
5. A worker establishes PostgreSQL tenant context, verifies the review belongs to that tenant, and atomically claims the queued review.
6. LangGraph retrieves tenant-scoped evidence through pgvector, calls the configured chat model, validates the structured report, and stores a workflow checkpoint.
7. The report transitions to `awaiting_review`; an authorized reviewer approves, rejects, or requests changes.

## Code boundaries

- `domain`: review state machine, domain entities and deterministic policies.
- `application`: use cases, ports, ingestion orchestration and schemas.
- `adapters`: SQLAlchemy repositories, LLM and embedding provider implementations.
- `api`: HTTP endpoints and dependency wiring.
- `agents`: LangGraph workflow and bounded research tools.
- `workers`: Celery task execution and transactional outbox publication.

## Important patterns

- Hexagonal architecture / ports and adapters.
- Repository and unit-of-work style transaction boundaries.
- Strategy for model and embedding providers.
- Explicit state machine for human review.
- Tenant-scoped idempotency using a canonical request hash.
- Transactional outbox with at-least-once publication.
- Atomic worker claim plus a ten-minute processing lease to recover stale running jobs.
- PostgreSQL RLS as defence in depth, in addition to explicit tenant predicates.
- Structured output and evidence-ID guardrails.

## Current workflow boundary

The shipped LangGraph graph is deliberately bounded: `retrieve_evidence -> research_and_risk -> END`. The handoff classifier is a deterministic routing hint, not a complete supervisor with autonomous specialist agents. The checkpoint table stores completed workflow state, not a LangGraph-native resumable checkpoint. For graph-level resume/interrupt semantics, add `langgraph-checkpoint-postgres`, configure a stable `thread_id`, and test interruption/resume against PostgreSQL.

## Retrieval boundary

The database uses `Vector(384)` and a cosine HNSW index. Local mock mode uses deterministic hash embeddings, which are not semantic. Set `MOCK_MODE=false` and configure an OpenAI-compatible embedding endpoint before claiming semantic retrieval quality. Production should add hybrid lexical/vector retrieval, reranking, source-specific freshness policies, and claim-level citation entailment evaluation.
