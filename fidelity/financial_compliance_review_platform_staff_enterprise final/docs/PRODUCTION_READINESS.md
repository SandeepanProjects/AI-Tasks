# Production-readiness gate (must be completed by the adopting team)

## Identity and authorization
- Replace local HS256 with OIDC/JWKS verification, key rotation, issuer/audience allowlists.
- Map IdP groups/roles to explicit permissions; enforce permission at route and tool boundary.
- Enforce reviewer separation-of-duties (creator cannot approve own review) and step-up auth for
  high-risk approvals.
- Add token revocation/session strategy and rate limits.

## PostgreSQL / pgvector
- Apply RLS policies and use a non-owner application role (no BYPASSRLS).
- Set tenant context transaction-locally; verify pool reuse cannot leak context.
- Add HNSW/IVFFlat index appropriate to corpus size and measured recall/latency.
- Use migrations for extension, schema, indexes, constraints, RLS, grants, and append-only audit.
- Define retention, encryption, PITR, backup restore drills, and connection-pool budgets.
- Ensure vector dimensions exactly match configured embedding model.

## Workflow and HITL
- Use durable PostgreSQL checkpointer; run its setup/migrations as deployment step, not per request.
- Store the canonical thread ID in the review record; never accept it from a client.
- Enforce state-machine transitions and idempotency for decisions.
- Persist reviewer identity, rationale, timestamp, and assessment version in audit records.
- Add timeout/escalation for stuck reviews and test restart/resume after process termination.

## LLM / guardrails
- Structured output schema validation; evidence must map to retrieved tenant-scoped policy versions.
- Add quote normalization strategy or exact source offsets; do not accept model-invented citations.
- Add PII/DLP screening, prompt-injection regression corpus, content limits, token budgets,
  model timeout/retry/circuit breaker, and provider fallback policy.
- Treat retrieved documents as untrusted; no side-effect tools in the review graph.
- Measure retrieval recall, evidence precision, citation validity, abstention, reviewer override rate.

## Reliability / operations
- Add transactional outbox for reliable event publication and idempotent Celery tasks.
- Configure OpenTelemetry traces, RED metrics, structured logs, correlation IDs, SLOs and alerts.
- Add load tests, chaos tests, dependency/container scanning, SBOM, SAST, penetration test.
- Add runbooks for provider outage, queue backlog, DB saturation, checkpoint recovery, and rollback.

## Hardening changes in 3.1.0

The 3.1.0 revision adds the following implementation changes:

- Tenant context is set transaction-locally for authenticated API database sessions and every worker database session. The runtime database role must remain subject to RLS (do not grant `BYPASSRLS`).
- Review creation and reviewer decisions persist their audit event and an outbox event in the same PostgreSQL transaction. The Celery Beat publisher delivers pending events; delivery is at-least-once, so worker claims and graph thread IDs are idempotency boundaries.
- Review creation accepts an optional `Idempotency-Key` header. Keys are scoped by tenant and bound to a canonical request hash; reusing a key with a different body returns HTTP 409.
- Reviewer decisions use row locking and a conditional lifecycle transition. The review creator cannot decide their own review.
- One lifecycle transition map is authoritative: queued -> running -> needs_human -> decision_queued -> resuming -> approved/rejected. Failed is reachable from active states; terminal states cannot be reopened.
- Worker leases and Celery task IDs prevent concurrent duplicate execution and allow redelivery of the same Celery task ID after worker loss. Python exceptions release the lease so retry can resume from the LangGraph checkpoint; exhausted retries persist a terminal failed state and audit event.
- LangGraph evaluation rework is explicitly bounded and increments a persisted counter. Rework resets the specialist outputs and task statuses; it cannot loop forever.
- Evaluation now rejects missing specialist outputs, empty policy context, findings without evidence, and evidence references outside the retrieved policy set. Guardrails still verify tenant, policy version, and exact quote substrings.
- Policy ingestion stores a document hash, chunk index, and optional source URI; a same-version/same-content upload is idempotent, while different content under the same code/version is rejected. New versions deactivate earlier versions while retaining historical records.
- Retrieval uses reciprocal-rank fusion across lexical and vector retrieval, with visible structured warnings when vector retrieval falls back to keyword search.
- Added audit-read endpoint, request correlation IDs, and Celery Beat service in Compose.

### Required deployment steps

1. Copy `.env.example` to `.env` and `.env.runtime.example` to `.env.runtime`. Set distinct strong values for `POSTGRES_ADMIN_PASSWORD`, `APP_DB_PASSWORD`, and `JWT_SECRET`; use the same app password in the runtime database URLs. Do not use sample secrets outside local development.
2. For a fresh Docker volume, start PostgreSQL and Redis. The PostgreSQL init script creates `app_user` as `NOSUPERUSER NOBYPASSRLS`, grants schema access, and creates the pgvector extension as the administrator. The API/worker use only `app_user`; they do not receive the PostgreSQL administrator password.
3. Run `docker compose up --build -d`. The one-shot `migrate` service applies Alembic migrations as `app_user` before API/worker/Beat start. `app_user` owns the application tables but remains subject to RLS because migrations enable `FORCE ROW LEVEL SECURITY`; it must never be granted `BYPASSRLS` or superuser.
4. Verify `docker compose ps` shows the migration service exited successfully and API/worker/Beat are running. Keep exactly one Celery Beat instance.
5. Configure a real OpenAI key for policy embeddings and LLM specialists. Without it, embedding ingestion returns a service-unavailable response and specialist behavior may use the existing deterministic fallback.
6. Run tests with `pip install -e '.[dev]'` and `pytest -q`.

### Verification boundary

If you already have a persistent PostgreSQL volume from the earlier Compose configuration, the init script will not rerun automatically. Create the non-superuser `app_user` role and grants manually, update `.env.runtime`, and verify `SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = 'app_user'` returns `false, false` before using the upgraded service.

The repository's unit tests do not prove PostgreSQL RLS isolation, outbox crash windows, Redis broker recovery, Celery redelivery, LangGraph checkpoint restoration, or concurrent reviewer behavior. Those require integration tests against real PostgreSQL/Redis and a multi-process worker deployment. Before production, run the tenant-isolation, outbox duplicate-delivery, worker-kill/restart, graph-resume, and concurrent-decision scenarios described in `OPERATIONS.md`. The outbox is intentionally not protected by tenant RLS because the internal publisher must scan events across tenants; it is not exposed through public API routes and must remain accessible only to the trusted service database role.
