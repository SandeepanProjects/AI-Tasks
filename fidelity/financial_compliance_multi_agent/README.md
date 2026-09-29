# Financial Compliance Multi-Agent Review Platform

Runnable reference application for reviewing financial communications against approved policies.

## Included
- FastAPI review/policy/decision/audit APIs
- LangGraph multi-agent flow: Claim Extraction → Policy Research → Compliance Analysis → Risk Assessment → Guardrails
- Explicit tools: semantic/keyword policy search, exact policy-code lookup, evidence packaging
- PostgreSQL + pgvector, Redis retrieval cache, Celery async review worker
- Human approval gate and audit events
- Tenant-scoped retrieval, role checks, schemas, tests, evaluation examples
- Docker Compose: API, pgvector PostgreSQL, Redis, Celery

## Quick start
1. `cp .env.example .env`; set `OPENAI_API_KEY` for model-backed extraction/analysis and embeddings.
2. `docker compose up --build`
3. Open http://localhost:8000/docs
4. Seed sample policies: `curl -X POST http://localhost:8000/api/v1/policies/seed -H 'Authorization: Bearer demo-admin'`
5. Create a review with `POST /api/v1/reviews` using `Bearer demo-reviewer` and JSON `{"content":"Our product guarantees 15% annual returns with no risk.","tenant_id":"demo"}`.
6. Run via `POST /api/v1/reviews/{id}/run` or enqueue via `/enqueue`; inspect the review; an approver uses `POST /api/v1/reviews/{id}/decision` with `Bearer demo-approver` and `{"decision":"rejected","comment":"Requires substantiation."}`.

## Local development
Python 3.11+, PostgreSQL with pgvector, Redis: `pip install -r requirements.txt`, configure `.env`, then `uvicorn app.main:app --reload`.

## Workflow
`POST review → ReviewService → LangGraph → claim extraction → policy research tools → analysis → risk → citation/schema guardrails → pending_approval → human decision + audit`.

## Important limitations
This is a portfolio/reference scaffold, not a certified compliance system. Demo bearer tokens are not production authentication. Replace with OIDC/JWT validation, tenant authorization, secrets management, reviewed Alembic migrations, full telemetry, rate limits, provider retries/timeouts, PII controls, and security/load tests. Model output is decision support; human approval is required. `create_all` is local bootstrap only. Without an API key, deterministic fallback logic and keyword retrieval are used. See `ARCHITECTURE.md`.

# Financial Compliance Multi-Agent Platform

Complete project ZIP · 59 project files · FastAPI + LangGraph + PostgreSQL/pgvector + Redis + Celery

Download the complete project ZIP

ZIP integrity verified

Python syntax compilation passed

## What’s included

Multi-agent LangGraph workflow

Claim Extraction → Policy Research → Compliance Analysis → Risk Assessment → Guardrails

Explicit tools

Policy search, policy-code lookup, and claim-evidence extraction. The research agent uses the retrieval and evidence tools.

Data and retrieval

PostgreSQL, pgvector embeddings, policy ingestion, tenant-scoped retrieval, and Redis caching.

Compliance controls

Output-schema validation, citation provenance checks, role checks, human approval/rejection, and audit events.

Application infrastructure

FastAPI, Celery background worker, Docker Compose, health endpoints, tests, and evaluation examples.

## Run it

1. Download and extract the ZIP.

2. Open the project directory in your IDE.

3. Copy `.env.example` to `.env`. Add your OpenAI API key if you want model-based analysis and embeddings.

4. Start the application:

Bash

```
docker compose up --build
```

5. Open the API documentation at [http://localhost:8000/docs](http://localhost:8000/docs) .

The `README.md` contains the setup instructions, example API requests, workflow, and endpoint list. `ARCHITECTURE.md` explains the modules and how the agents and tools fit together.

Important: This is a complete runnable reference implementation, but it is not yet a hardened production compliance system. Authentication uses demo bearer tokens; production deployment still needs real identity integration, reviewed database migrations, stronger operational controls, and security testing. The README documents these limitations.
