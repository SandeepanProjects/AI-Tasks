# Production roadmap

The generated repository is a runnable architectural reference. For a full
production financial platform, add:

1. OIDC/JWKS authentication, token rotation and service identity.
2. Alembic migrations per application and PostgreSQL RLS for tenant isolation.
3. Application-owned repositories and domain models.
4. pgvector/Qdrant adapters, embedding service, BM25 + vector hybrid retrieval,
   reranking, document versioning and citation IDs.
5. LangGraph adapter with durable PostgreSQL checkpoints, interrupt/resume HITL,
   conditional routing, max-step limits, retries and evaluator/rework loops.
6. PII detection/redaction, structured-output validation, citation enforcement,
   prompt-injection detection and domain policy guardrails.
7. Celery idempotency, retries and dead-letter strategy for long-running jobs.
8. OpenTelemetry traces, token/cost metrics, workflow correlation and audit events.
9. Kubernetes/Helm/Terraform, secrets manager, network policies and autoscaling.

Do not move business logic into infrastructure packages just because the platform grows.
