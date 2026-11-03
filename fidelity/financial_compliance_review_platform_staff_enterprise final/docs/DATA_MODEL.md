# Data model notes

- `policies`: tenant-scoped policy chunks and embeddings; use immutable policy versions.
- `reviews`: workflow aggregate and canonical LangGraph thread identifier.
- `audit_events`: append-only security/compliance trail.
- LangGraph checkpoint tables: durable graph state and interrupt resume.

For production, add explicit foreign keys, idempotency keys, reviewer decision records, policy
ingestion job/outbox tables, vector index tuning, and retention partitions based on workload.
Do not make audit records mutable by the application role.
