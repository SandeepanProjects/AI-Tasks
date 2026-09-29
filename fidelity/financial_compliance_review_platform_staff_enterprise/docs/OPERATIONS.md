# Deployment and operations checklist

- Replace sample HS256 authentication with OIDC/JWKS; validate issuer, audience, expiry, tenant and roles.
- Put secrets in a managed secret store; enable TLS everywhere.
- Add transactional outbox + dispatcher for reliable DB-to-queue delivery.
- Configure queue retry ceilings, task time limits, dead-letter queue and poison-message alerts.
- Enable PostgreSQL PITR/backups and Redis HA; regularly test restoration.
- Define PII minimization, encryption, retention, deletion and audit immutability.
- Benchmark pgvector indexes (HNSW/IVFFlat) and query plans with representative tenant data.
- Add distributed tracing, metrics for queue lag, graph duration, LLM tokens/cost, retrieval fallback and HITL wait time.
- Add integration tests for durable pause/resume across worker restart and concurrent duplicate reviewer submissions.
- Run threat modeling for prompt injection, tenant isolation, policy poisoning and unsafe tool access.
