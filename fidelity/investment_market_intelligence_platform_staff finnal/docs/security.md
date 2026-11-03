# Security model

- Tenant identity is derived from verified token claims; request bodies cannot select a tenant.
- OIDC mode verifies RS256 tokens against a cached JWKS document and checks issuer, audience, expiry, subject, tenant and role claims. Confirm the exact claim mapping with the identity provider.
- Local HS256 authentication is development-only and is rejected when `APP_ENV=production`.
- RLS policies protect reviews, evidence chunks, idempotency records, audit events and workflow checkpoints. Repositories also apply explicit tenant predicates and transaction-local `app.tenant_id` context.
- Celery task payload includes tenant scope; worker applies RLS before reading the row and verifies both review ID and tenant ID.
- Review jobs are claimed atomically; duplicate queue deliveries cannot run concurrently. A processing lease allows stale jobs to be reclaimed after worker death.
- Idempotency is tenant-scoped and request-hash-aware. Reusing a key with a different request returns conflict.
- Retrieved evidence is untrusted input. It cannot authorize tools or override system policy.
- The LLM cannot directly run SQL, shell commands, arbitrary URL fetches, trades, or wallet operations.
- Report schema, citation IDs, limitations and prohibited certainty claims are validated before HITL.
- Audit records capture creation, processing and reviewer decisions. For regulated environments, export them to immutable storage/SIEM with retention controls.
- Do not expose `/metrics` publicly without network restrictions or an authenticated metrics gateway.

## Deployment notes

Use a dedicated non-superuser database role, private networking, TLS, managed secrets, key rotation, encryption at rest, backup/PITR, least-privilege IAM, and container/dependency scanning. Validate RLS with a real PostgreSQL integration test using the exact application role; unit tests cannot establish tenant isolation.
