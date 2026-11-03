# Investment Market Intelligence Platform — Staff Engineer Edition

A reference implementation of a tenant-isolated, evidence-grounded investment research workflow. It demonstrates production-oriented backend and AI engineering patterns: hexagonal architecture, asynchronous processing, PostgreSQL/pgvector retrieval, LangGraph orchestration, human approval, tenant-scoped authorization, audit records, and operational observability.

> **Important:** This is an engineering reference project, not a regulated investment product. It does not execute trades or provide personalized investment advice. Before production use, complete the deployment, model-risk, data-licensing, security, and compliance gates in `docs/production_readiness.md`.

## Architecture

```text
Client
  │ HTTPS + bearer token + Idempotency-Key
  ▼
FastAPI ── AuthN/AuthZ ── Request validation
  │
  ├── PostgreSQL transaction: review + idempotency record + outbox event
  │
  └── Best-effort Celery dispatch
          │
          ├── Celery Beat outbox publisher (recovers failed dispatch)
          ▼
      Review worker ── tenant context / RLS
          │
          ▼
      LangGraph workflow
          ├── tenant-scoped evidence retrieval (pgvector)
          ├── structured LLM research and risk analysis
          └── citation / schema / prohibited-claim guardrails
          │
          ▼
      PostgreSQL: report + checkpoint + audit
          │
          ▼
      AWAITING_REVIEW ── authorized human decision ── APPROVED / REJECTED
```

## What is implemented

- Domain/application/adapter separation with ports and adapters.
- FastAPI API with JWT development authentication and OIDC/JWKS verification mode.
- PostgreSQL persistence with SQLAlchemy 2.x and Alembic migrations.
- PostgreSQL row-level security for reviews, evidence, idempotency keys, audit events, and workflow checkpoints.
- Tenant-scoped request idempotency using `(tenant_id, key)` plus a canonical request hash.
- Transactional outbox: review creation and dispatch event commit in one database transaction; Celery Beat republishes pending events if Redis dispatch fails.
- Atomic worker claim to prevent duplicate Celery deliveries from processing the same queued review concurrently.
- Redis/Celery asynchronous processing with retry handling for transient network/timeouts.
- Evidence ingestion endpoint with chunking, content hashes, source-aware deduplication, embeddings, and pgvector persistence.
- OpenAI-compatible embedding and chat adapters; deterministic embeddings and mock chat are development-only.
- LangGraph research workflow with bounded retrieval tools, tenant scoping, structured output, evidence citation validation, and source provenance metadata.
- Human review state machine and append-only audit event records.
- Prometheus metrics for requests, review jobs, retrieval hits/misses, LLM calls/latency/token usage; structured logs, correlation IDs, dependency readiness, Docker Compose, and tests.

## Known boundaries — do not misrepresent these in interviews

- The current graph is a bounded two-node workflow (`retrieve_evidence` → `research_and_risk`), not a sophisticated autonomous multi-agent system. Handoff classification is a routing hint; independent specialist agents and supervisor loops are extension points.
- The application checkpoint table records completed workflow state. It is **not** a LangGraph-native node-level resumable checkpointer. For true graph resume/interrupt semantics, integrate and test `langgraph-checkpoint-postgres` and use a stable `thread_id` per review.
- Deterministic hash embeddings are for local tests only. Set `MOCK_MODE=false` and configure a real embedding model before evaluating semantic retrieval.
- The included evidence endpoint ingests text. PDF/HTML parsers, licensed market-data connectors, source scheduling, and source-specific freshness SLAs must be added for a real market-data product.
- The project includes basic RLS policies and tenant context propagation. Validate them with the actual non-owner application DB role and real PostgreSQL integration tests; local SQLite/unit tests cannot prove RLS isolation.
- The outbox publisher is intentionally at-least-once. Consumers must remain idempotent. Review processing uses an atomic database claim.
- The OIDC verifier supports RS256 JWKS. Confirm claim mapping, key rotation, issuer/audience values, and provider-specific role claims with your identity provider.
- LLM citation-ID validation proves that cited IDs were retrieved; it does not prove that each sentence is semantically entailed by the cited text. Add claim-level citation entailment evaluation before regulated use.

## Quick start

Requirements: Docker Compose, Python 3.12+, and a local `.env` file.

```bash
cp .env.example .env
# Set JWT_SECRET to a random value of at least 32 characters, for example:
# python -c 'import secrets; print(secrets.token_urlsafe(48))'
# Paste the generated value into .env before starting the stack.
docker compose up --build
```

Compose starts PostgreSQL/pgvector, Redis, a one-shot migration service, API, Celery worker, and Celery Beat. API docs: `http://localhost:8000/docs`.

To run locally without Dockerized API/worker:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
celery -A app.workers.celery_app.celery_app worker -Q reviews,outbox --loglevel=INFO
celery -A app.workers.celery_app.celery_app beat --loglevel=INFO
```

Seed a development-only evidence fixture after migrations and create a local test token:

```bash
python -m scripts.seed_demo_evidence
python scripts/create_dev_token.py
```

The development token grants analyst/reviewer/admin roles for `demo-tenant`. Do not use this token-generation flow outside local development.

## API

- `POST /v1/evidence/ingest` — admin-only tenant-scoped text ingestion.
- `POST /v1/reviews` — create a research review; requires `Idempotency-Key`; returns `202`.
- `GET /v1/reviews/{review_id}` — retrieve the tenant-owned review; analysts see the report only after approval, reviewers/admins can inspect pending reports.
- `POST /v1/reviews/{review_id}/decision` — reviewer/admin approval, rejection, or change request.
- `POST /v1/reviews/{review_id}/retry` — admin-only requeue of a failed review with a new outbox event.
- `GET /health/live` and `GET /health/ready` — liveness and PostgreSQL/Redis readiness.
- `GET /metrics` — Prometheus metrics.

Example create request:

```bash
curl -X POST http://localhost:8000/v1/reviews \
  -H 'Authorization: Bearer <access-token>' \
  -H 'Idempotency-Key: demo-review-001' \
  -H 'Content-Type: application/json' \
  -d '{"question":"Summarize the key risk factors for BTC using available evidence","scope":{"assets":["BTC"],"lookback_days":30},"purpose":"risk_review"}'
```

## Configuration

See `.env.example`. Important controls:

- `MOCK_MODE=true` uses deterministic local adapters; never use this for production.
- `MOCK_MODE=false` requires `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`, and `EMBEDDING_MODEL`.
- `EMBEDDING_DIMENSIONS` is fixed at 384 because the database vector column is `Vector(384)`. Changing it requires a database migration and re-embedding.
- `AUTH_MODE=local_jwt` is development-only. Production requires `AUTH_MODE=oidc`, `OIDC_JWKS_URL`, issuer, and audience.
- `JWT_SECRET` must be random and at least 32 characters for local token signing.

## Quality checks

```bash
ruff check .
pytest -q
python -m compileall -q app migrations tests scripts
```

See `docs/api_examples.md` for a complete local API walkthrough, and `docs/architecture.md`, `docs/security.md`, `docs/runbook.md`, and `docs/production_readiness.md` for design details and operational gates.
