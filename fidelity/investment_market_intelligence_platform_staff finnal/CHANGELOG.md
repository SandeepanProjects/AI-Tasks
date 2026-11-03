# Changelog

## Staff hardening pass

- Added request-hash-aware tenant-scoped idempotency.
- Added a transactional outbox, scheduled republishing, atomic worker claims, processing leases, transient retry handling, and admin retry endpoint.
- Fixed worker RLS context propagation before review lookup.
- Made review creation, reviewer decisions, worker completion/failure, and retry audit records transactional with their state changes where implemented.
- Added tenant RLS for idempotency, audit, and workflow checkpoint records.
- Added tenant/time-window-scoped evidence retrieval, full-text search for mock mode, pgvector semantic search for configured providers, and source provenance in generated reports.
- Added text evidence ingestion, source-aware deduplication, embeddings, HNSW and full-text indexes.
- Added OIDC/JWKS RS256 verification mode and made local HS256 development-only.
- Added analyst report visibility controls until reviewer approval.
- Added model latency/token metrics, retrieval metrics, improved readiness, correlation ID sanitization, and worker event-loop/async-engine lifecycle handling.
- Added Docker Compose migration, worker and Beat services; API walkthrough, architecture/security/runbook/production-readiness documentation; and expanded unit tests.

## Known remaining production gates

See `docs/production_readiness.md`. In particular, the current LangGraph checkpoint table stores completed state only; a LangGraph-native resumable Postgres checkpointer, PostgreSQL/Redis/Celery integration tests, licensed data connectors, semantic RAG evaluation, rate limiting, and production observability/security validation remain required before real customer or regulated financial use.
