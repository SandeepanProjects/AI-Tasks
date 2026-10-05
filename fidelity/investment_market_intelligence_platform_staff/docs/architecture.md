# Architecture

## Boundaries

**API layer**: HTTP, authentication, request validation, correlation IDs.

**Application layer**: use cases and ports. No SQLAlchemy or FastAPI business logic.

**Domain layer**: review lifecycle, policy rules, guardrails.

**Adapters**: PostgreSQL, Redis/Celery, LLM, embeddings, external market-data providers.

**Agents**: LangGraph orchestration and typed tools. Retrieved text is untrusted data.

## Patterns

- **Hexagonal / Ports & Adapters**: `application/ports.py` defines contracts; adapters implement them.
- **Repository**: `SqlReviewRepository` and evidence/audit repositories hide persistence.
- **Strategy**: `ChatModel` and `EmbeddingProvider` permit vendor replacement.
- **Planner/Supervisor boundary**: `choose_handoff()` provides bounded, deterministic routing. The current graph deliberately avoids unconstrained autonomous recursion.
- **Evaluator/guardrail**: report validation checks schema semantics, citation integrity and prohibited claims before the report reaches HITL.
- **State machine**: review status transitions are explicit and reject illegal transitions.
- **Idempotency**: DB uniqueness prevents duplicate create requests.
- **HITL**: approval is a durable application state, not a UI-only flag.
- **Checkpointing**: workflow state is persisted after completion. For true node-level interrupt/resume, a supported LangGraph Postgres checkpointer can be introduced without changing the domain/application ports.

## Why Celery

The API must not hold an HTTP request open while LLM/RAG work runs. It persists the command, enqueues a job, and returns 202. Workers own long-running execution and retry boundaries.
