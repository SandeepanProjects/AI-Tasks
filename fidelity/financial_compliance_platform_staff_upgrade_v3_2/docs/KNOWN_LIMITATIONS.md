# Known limitations — do not skip

This is an advanced reference project, not a turnkey regulated deployment.

1. The starter API surface in the supplied v2 archive is incomplete; inspect `app/main.py` and add
   endpoint wiring appropriate to your deployment. The new RBAC module is a reusable policy seam.
2. Configure tenant context inside the same transaction as each protected query. RLS policies
   require this and a non-owner runtime role. Test under actual PostgreSQL roles.
3. The existing workflow needs integration validation for your exact LangGraph/checkpointer version.
   Exercise interrupt → process restart → authorized resume with a real PostgreSQL checkpointer.
4. Add separation-of-duties and idempotent decision persistence before production.
5. The sample model/retrieval logic requires evaluation, prompt-injection testing, cost controls,
   timeouts, and provider outage handling.
6. A production event pipeline should use a transactional outbox; Celery tasks must be idempotent.

## Remaining production work after 3.1.0

- Add automated PostgreSQL integration tests using a non-owner, non-`BYPASSRLS` role for every tenant-scoped table, including idempotency records.
- Add fault-injection tests for outbox send-before-commit duplicates, Redis outages, worker process termination, expired leases, and LangGraph checkpoint recovery.
- Add end-to-end OTel traces/metrics/exporters, dashboards, alerting, and token/cost budgets. Current observability is structured logs plus request IDs, not a complete OpenTelemetry deployment.
- Add a production identity provider / centralized policy engine; the role-to-permission map is currently local deterministic configuration.
- Add document parsers (PDF/HTML), OCR, malware scanning, content-type validation, and source access controls. Ingestion currently accepts extracted text from the API.
- Add cross-encoder reranking and a curated retrieval/evaluation corpus. Hybrid retrieval is currently RRF over keyword and vector results.
- Add claim-level entailment evaluation and an independently reviewed compliance benchmark. Exact quote matching verifies provenance, not semantic entailment.
- Add API rate limiting, per-tenant quotas, provider circuit breakers, dead-letter queue operations, and formal retention/deletion policies.
- Use a dedicated internal publisher DB role and network boundary for the outbox service in hardened deployments. Do not expose the outbox table to application users.
- Configure and verify production backup/restore, encryption at rest/in transit, secrets management, key rotation, and disaster recovery.
