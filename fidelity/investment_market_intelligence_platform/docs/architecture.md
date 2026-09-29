# Architecture and runtime flow

## Request lifecycle
1. FastAPI validates JSON using Pydantic.
2. JWT verifier builds a `Principal` with subject, tenant, and roles.
3. Application use case validates business rules and derives tenant from the principal.
4. Repository persists the review. The reference wiring uses an in-memory adapter; swap it for SQLAlchemy repository in deployment.
5. LangGraph executes retrieval and structured analysis with a stable thread ID.
6. Guardrails validate required fields, evidence IDs, uncertainty, and prohibited certainty language.
7. Review enters `awaiting_review`; reviewer endpoint enforces reviewer/admin role.
8. Decision and reviewer identity are stored. Production should write an immutable audit event and publish only approved outputs.

## Patterns
- **Ports and adapters / hexagonal**: `application/ports.py` defines contracts; `adapters/` supplies implementations.
- **Repository**: hides persistence details from use cases.
- **Dependency injection**: FastAPI dependencies construct service and adapters.
- **Strategy**: `ChatModel` and `MarketDataProvider` allow provider substitution.
- **Factory/composition root**: `api/dependencies.py` wires the graph and service.
- **State machine**: `ReviewStatus` expresses lifecycle and legal transitions.
- **Command**: review create/decision requests are explicit commands.
- **Supervisor / specialist handoff**: `handoffs.py` routes research to evidence and risk stages; graph currently uses a compact combined analysis node.
- **Policy object**: `domain/policies.py` centralizes domain validation.
- **Idempotency**: `services/idempotency.py` supplies stable request fingerprints; wire to DB uniqueness/Redis lock.

## Staff-level trade-offs
- Keep model orchestration out of route handlers.
- Separate durable business state (PostgreSQL) from ephemeral coordination/cache (Redis).
- Treat LLM output as untrusted; schema validation alone is not factual validation.
- Store evidence provenance and snapshots so reports can be reproduced.
- Fail closed on missing market data, stale quotes, invalid citations, or unavailable reviewer authorization.
- Avoid autonomous execution: research generation and trade execution are separate trust domains.
