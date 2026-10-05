# Production readiness assessment

## Original ZIP: NOT production ready

Critical findings:

1. Runtime dependency injection used in-memory repositories and a mock LLM.
2. `ReviewService.create()` executed the workflow inline; Celery was not on the request path.
3. pgvector existed only as a column; no vector retrieval path was wired.
4. HITL was persisted after graph completion rather than implemented as durable graph interrupt/resume.
5. JWT code explicitly described itself as a demo and used a development secret default.
6. Readiness returned `ready` without checking PostgreSQL.
7. Idempotency was a helper, not an enforced DB operation.
8. Audit events were constructed in memory and not persisted.
9. The route module was missing the `UUID` import.
10. Agent handoff routing was computed but not actually used to execute specialist stages.
11. No SQLAlchemy repository existed for reviews.
12. RLS SQL existed as a standalone artifact but was not part of the migration path.
13. Tests covered only two small areas and did not exercise real persistence, API, queue, or workflow integration.

## Staff-level target

The refactored edition addresses the above with real database persistence, asynchronous worker execution, durable lifecycle transitions, repository/port boundaries, audit persistence, idempotency, health probes, observability, security hardening, and migration-managed RLS.

## Remaining go-live gates

This is **production-oriented reference code, not a certified production financial system**. Before deployment:

- replace local HS256 auth with enterprise OIDC/JWKS;
- configure licensed market-data and model providers;
- use a real semantic embedding model and ingestion pipeline;
- add integration/e2e tests against PostgreSQL, Redis and Celery;
- add rate limiting/WAF/API gateway controls;
- deploy secrets through a secret manager;
- configure TLS, network segmentation, encryption, backup/PITR and DR;
- add immutable audit export/SIEM integration;
- perform threat modeling, prompt-injection red teaming and dependency/SAST/container scans;
- validate model/vendor risk, data licensing and compliance requirements;
- use a true LangGraph Postgres checkpointer if node-level interrupt/resume is required;
- load test worker/API capacity and establish SLOs.
