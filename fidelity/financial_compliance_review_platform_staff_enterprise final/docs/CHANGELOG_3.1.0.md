# 3.1.0 — Reliability and security hardening

## Fixed
- Wired transaction-local tenant context into authenticated API and worker database sessions.
- Replaced the Compose superuser runtime connection with a dedicated `app_user` role created as `NOSUPERUSER NOBYPASSRLS`; the runtime role remains subject to forced row-level security.
- Unified lifecycle transitions and added the `resuming` state.
- Prevented reviewers from deciding their own reviews.
- Made review creation and decision dispatch transactional through an outbox.
- Added tenant-scoped idempotency keys and request-body conflict detection.
- Added worker leases/task-ID redelivery protection and terminal failure recording after retry exhaustion.
- Fixed the LangGraph rework counter and bounded retry route.
- Made agent output serialization JSON-safe before storing workflow state/results.
- Added checks for empty policy context, missing specialist outputs, unsupported evidence IDs, and findings without evidence.

## Improved
- Added policy document hashes, chunk indexes, source URI metadata, and version activation/deactivation.
- Added reciprocal-rank fusion over vector and keyword retrieval with explicit fallback logging.
- Added audit-read endpoint, request correlation IDs, and configurable outbox polling/batch sizes.
- Added PostgreSQL role bootstrap, separate Compose/runtime environment examples, an automatic migration service, and a Celery Beat service.
- Added unit tests for lifecycle transitions, evaluator evidence requirements, and stable idempotency request hashes.

## Verification
- `python -m compileall -q app migrations tests`: passed.
- `pytest -q`: 13 passed.
- PostgreSQL/Redis integration, migration execution, Celery redelivery, and LangGraph checkpoint crash recovery were not run in this build environment; these require the project dependencies and live services. See `PRODUCTION_READINESS.md` and `KNOWN_LIMITATIONS.md`.
