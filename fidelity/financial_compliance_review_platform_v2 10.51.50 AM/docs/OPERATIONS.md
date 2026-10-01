# Operations checklist
- Use managed PostgreSQL with TLS, backups/PITR, least-privilege DB role, and migration job.
- Use Redis ACL/TLS, private networking, queue monitoring, worker timeouts, dead-letter/replay policy.
- Configure JWT/OIDC issuer, audience, JWKS rotation, token expiry, role/tenant claims; never ship dev token.
- Store secrets in a secret manager; scan dependencies, images, source, and IaC.
- Define retention/deletion for prompts, outputs, audit logs, and checkpoints.
- Add rate limits, request size limits, model budgets, provider timeouts, circuit breakers and cost alerts.
- Add tenant-isolation tests for every repository/tool; run threat modeling and security tests.
- Monitor API latency, queue depth, workflow duration, retrieval-empty rate, agent failures, guardrail blocks,
  human approval latency, token/cost metrics, and DB/Redis health.
- Version policies immutably and record policy version in each review result.
- This reference does not yet wire durable LangGraph checkpoint/resume or interrupt-based HITL.
  Human decisions are persisted at the API layer. Add AsyncPostgresSaver + interrupt/Command resume before
  describing the workflow as durable resumable HITL.
- Specialists and evaluator are rule-based/completeness-oriented. Validate with labeled data and domain experts.
