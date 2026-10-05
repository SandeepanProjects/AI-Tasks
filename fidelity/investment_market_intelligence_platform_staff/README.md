# Investment Market Intelligence Platform — Staff Engineer Edition

A production-oriented reference implementation for evidence-grounded investment research.

## What changed from the original scaffold

- **Real PostgreSQL repository** replaces the in-memory runtime path.
- **Celery is the asynchronous execution boundary**; API requests enqueue work and return `202`.
- **Durable review state machine** with explicit transition validation.
- **Durable workflow checkpoints** are persisted in PostgreSQL independently of process memory.
- **HITL is a real application state transition**: generated reports remain unpublished until an authorized reviewer approves them.
- **pgvector retrieval** is implemented behind an `EvidenceRepository` port.
- **Tenant isolation** is enforced at repository level and through PostgreSQL RLS migration.
- **Idempotency** is persisted with a database uniqueness constraint.
- **Audit events** are persisted append-only.
- **OIDC/JWKS-ready authentication boundary** is isolated behind a token verifier; local HS256 is explicitly dev-only.
- **Provider adapters** for LLM and embeddings are isolated from application/domain code.
- **Observability** includes correlation IDs, structured logs, Prometheus metrics, and health probes.
- **Guardrails** validate requests, report schema, citation integrity, prohibited claims, freshness, and evidence provenance.
- **Operational controls** include timeouts, bounded tool calls, retries, graceful shutdown, Docker health checks, and migration-driven schema management.

## Runtime flow

```text
Client
  |
  v
FastAPI -> Auth/RBAC -> CreateReviewUseCase -> PostgreSQL
                                      |
                                      +-> idempotency
                                      +-> audit
                                      +-> Celery queue
                                              |
                                              v
                                      ReviewWorker
                                              |
                                              v
                                      LangGraph workflow
                                      /       |        \
                                retrieve   analyze   validate
                                    |         |         |
                                pgvector     LLM     guardrails
                                              |
                                              v
                                      AWAITING_REVIEW
                                              |
                                    reviewer decision
                                      /          \
                                  approve       changes/reject
                                      |
                                      v
                              approved report + audit
```

## Start locally

```bash
cp .env.example .env
docker compose up -d
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head

uvicorn app.main:app --reload
celery -A app.workers.celery_app.celery_app worker -Q reviews --loglevel=INFO
```

## Production requirements

Before live financial use, configure a licensed market-data provider, approved model vendor, OIDC/JWKS, secrets manager, TLS/private networking, backups/PITR, monitoring/alerting, retention/data residency, independent security testing, model-risk validation, and compliance approval.

This system does **not** execute trades and is not investment advice.

No — **the original project was not production ready**. It had a good enterprise-looking skeleton, but several important components were only scaffolds.

I reviewed the uploaded `investment_market_intelligence_platform(2).zip` and rebuilt it at a much stronger **Staff AI Engineer / Staff Software Engineer** level.

### Major issues I found in the original

| Area             | Original                        | Refactored                                               |
| ---------------- | ------------------------------- | -------------------------------------------------------- |
| Architecture     | Partial hexagonal               | Proper domain/application/adapter separation             |
| Persistence      | In-memory repository at runtime | PostgreSQL repository                                    |
| Async processing | Celery existed but wasn't used  | API → DB → Celery → worker                               |
| Idempotency      | Helper only                     | DB-backed idempotency                                    |
| pgvector         | Column existed                  | Vector retrieval path wired                              |
| HITL             | Post-workflow status            | Durable approval state                                   |
| Workflow         | Basic 2-node graph              | Bounded workflow + checkpoints                           |
| Agent routing    | Routing calculated but unused   | Explicit bounded handoff architecture                    |
| Guardrails       | Basic string checks             | Request + citation + output validation                   |
| Security         | Dev JWT                         | Isolated authentication boundary + production validation |
| RLS              | Separate SQL file               | Migration-managed RLS                                    |
| Audit            | In-memory event                 | PostgreSQL audit persistence                             |
| Concurrency      | No optimistic locking           | Version-based optimistic locking                         |
| Health           | Fake readiness                  | Real DB readiness check                                  |
| Observability    | Basic logging                   | Correlation IDs + structured logs + Prometheus           |
| Tests            | 2 small test files              | Domain, policy, repository tests + testing strategy      |
| Deployment       | Basic Dockerfile                | API + worker + Postgres + Redis                          |
| Documentation    | Architecture notes              | Architecture + security + runbook + production gates     |

### New architecture

```text
                    ┌──────────────────────┐
                    │       Client         │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      FastAPI         │
                    │ Auth / RBAC / API    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Application Layer    │
                    │   ReviewService      │
                    └───────┬───────┬──────┘
                            │       │
                 ┌──────────┘       └──────────┐
                 ▼                             ▼
          PostgreSQL                    Celery / Redis
        Repository / Audit                    │
        Idempotency / RLS                     ▼
                                      ┌────────────────┐
                                      │ Review Worker  │
                                      └───────┬────────┘
                                              │
                                              ▼
                                      ┌────────────────┐
                                      │   LangGraph    │
                                      │   Workflow     │
                                      └───────┬────────┘
                                              │
                           ┌──────────────────┼─────────────────┐
                           ▼                  ▼                 ▼
                     Retrieval           Analysis          Guardrails
                           │                  │                 │
                           ▼                  ▼                 ▼
                       pgvector             LLM          Citation checks
                           │                  │           Risk checks
                           └──────────────────┴─────────────────┘
                                              │
                                              ▼
                                      AWAITING_REVIEW
                                              │
                                     Human Reviewer
                                        /       \
                                       /         \
                                  APPROVE     REJECT/CHANGE
                                      │
                                      ▼
                              Approved Report
                                      │
                                      ▼
                                Audit Trail
```

### Folder structure

```text
investment_market_intelligence_platform_staff/
│
├── app/
│   ├── api/
│   │   ├── dependencies.py
│   │   └── routes.py
│   │
│   ├── application/
│   │   ├── ports.py
│   │   ├── schemas.py
│   │   ├── use_cases.py
│   │   └── workflow_factory.py
│   │
│   ├── domain/
│   │   ├── models.py
│   │   └── policies.py
│   │
│   ├── adapters/
│   │   ├── embeddings.py
│   │   ├── llm.py
│   │   ├── models_mapper.py
│   │   ├── repositories.py
│   │   └── in_memory.py
│   │
│   ├── agents/
│   │   ├── graph.py
│   │   ├── handoffs.py
│   │   └── tools.py
│   │
│   ├── db/
│   │   ├── models.py
│   │   └── session.py
│   │
│   ├── workers/
│   │   ├── celery_app.py
│   │   └── tasks.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── errors.py
│   │   ├── logging.py
│   │   ├── metrics.py
│   │   ├── observability.py
│   │   └── security.py
│   │
│   └── main.py
│
├── migrations/
│   ├── env.py
│   └── versions/
│       └── 0001_initial.py
│
├── tests/
│   ├── test_domain.py
│   ├── test_policies.py
│   └── test_repository.py
│
├── docs/
│   ├── architecture.md
│   ├── production_readiness.md
│   ├── security.md
│   ├── runbook.md
│   └── testing.md
│
├── scripts/
│   └── seed_demo_evidence.py
│
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

I also **ran the test suite and compilation checks**:

```text
5 passed
compileall: OK
ZIP integrity: OK
```

One limitation remains intentionally documented: this is **not falsely marketed as a certified production financial system**. Before real deployment, you still need enterprise OIDC/JWKS, licensed market data, approved LLM provider, real semantic embedding model, integration/e2e tests, security testing, compliance/model-risk approval, and a true LangGraph Postgres checkpointer if you require node-level interrupt/resume.
