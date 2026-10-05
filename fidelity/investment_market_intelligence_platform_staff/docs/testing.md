# Testing strategy

## Unit
- domain lifecycle and legal transitions
- request/report guardrails
- repository tenant scoping with fakes

## Integration
Run PostgreSQL + pgvector + Redis and exercise migrations/RLS, CRUD, optimistic locking, idempotency, vector retrieval, Celery execution and health probes.

## End-to-end
Create review -> queued -> worker -> awaiting_review -> reviewer decision -> approved/rejected.

## Security
Run SAST, dependency/container/secret scans, authorization and tenant-breakout tests, prompt-injection corpus, SSRF tests for future connectors, and load tests.
