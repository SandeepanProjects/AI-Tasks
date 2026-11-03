# Production readiness assessment

## Hardening completed in this edition

- Runtime uses PostgreSQL repositories rather than in-memory repositories.
- API returns 202 and worker performs long-running research asynchronously.
- Review, idempotency record, creation audit and outbox event are committed atomically.
- Outbox publisher recovers broker dispatch failures; worker claim is atomic and has a stale-processing lease.
- Idempotency is scoped by tenant and request hash.
- Worker sets tenant context before reading RLS-protected reviews.
- RLS covers reviews, evidence, idempotency, audit and workflow checkpoints.
- Evidence ingestion chunks text, hashes content, deduplicates and stores embeddings.
- Real OpenAI-compatible embeddings and chat adapters are available; mock adapters are development-only.
- OIDC/JWKS verification mode is implemented; local HS256 is rejected in production.
- Report output is schema checked and citations must be from retrieved evidence.
- Docker Compose runs migrations, API, worker and Beat.
- Unit tests cover lifecycle, policies, tenant-scoped fake repository behavior, ingestion and report validation.

## Remaining go-live gates (mandatory)

This is production-oriented reference code, **not a certified production financial system**. Before real financial or customer use:

1. Run integration and end-to-end tests against PostgreSQL/pgvector and Redis/Celery using a non-superuser application DB role; explicitly test RLS bypass attempts and cross-tenant retrieval.
2. Add a true LangGraph PostgreSQL checkpointer for node-level resume and interrupt/resume. The current checkpoint table records completed state only.
3. Add licensed market-data connectors, source provenance validation, scheduled refresh, source-specific freshness SLAs and data-quality checks.
4. Configure a real embedding model; validate vector dimension; implement hybrid retrieval, reranking, and relevance/recall evaluation.
5. Add RAGAS or equivalent offline evaluation, retrieval Recall@K/Precision@K, citation entailment checks, regression datasets and deployment gates.
6. Add rate limiting, API gateway/WAF, request-size limits, abuse controls and per-tenant quotas.
7. Add OpenTelemetry traces across API, Celery, retrieval and model calls; configure alerting/SLOs and dashboards.
8. Add transactional reviewer decision + audit atomicity, immutable audit export, retention/deletion workflows and compliance approval.
9. Add provider circuit breakers, bounded retries, fallback models, token budgets, per-tenant spend limits and cache policy.
10. Add SAST, dependency/container/secret scans, threat model, penetration test, prompt-injection red-team corpus and disaster-recovery exercises.
11. Validate OIDC claims, key rotation and authorization mapping with the real identity provider.
12. Load test queue throughput, database pool sizing, model concurrency and p95/p99 latency; scale API and worker independently.

## Known design limitations

- The current LangGraph graph has two nodes; handoff classification is not a fully autonomous multi-agent supervisor.
- Deterministic embeddings in mock mode are not semantic and must not be used to assess RAG quality.
- Text ingestion is implemented; PDF/HTML parsing and external market-data connectors are not.
- Outbox delivery is at-least-once; duplicate events are expected and handled by atomic review claiming.
- Citation ID validation does not prove that every generated statement is entailed by its cited source.
