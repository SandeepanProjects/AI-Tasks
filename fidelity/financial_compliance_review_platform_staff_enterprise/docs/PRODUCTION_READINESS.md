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
