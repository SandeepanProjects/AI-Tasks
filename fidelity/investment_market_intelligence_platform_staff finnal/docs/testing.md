# Testing strategy

## Unit tests in this repository

- domain lifecycle and illegal transitions
- request/report guardrails
- tenant-scoped fake repository behavior
- ingestion chunking, embedding dimensions and empty-content rejection
- strict report contract and citation-ID validation

Run:

```bash
PYTHONPATH=. pytest -q
python -m compileall -q app migrations tests scripts
```

## Required integration tests before production

Run PostgreSQL with pgvector and Redis, apply Alembic migrations, and exercise:

- RLS with separate tenants and the exact non-superuser application DB role
- idempotency races, same-key/same-payload replay, and same-key/different-payload conflict
- transactional outbox behavior during Redis outage and publisher restart
- atomic worker claims, duplicate delivery, stale lease recovery and retry exhaustion
- vector ingestion/search, dimension mismatch and evidence deduplication
- audit creation and reviewer-decision consistency
- OIDC/JWKS key rotation, issuer/audience validation and role authorization
- full API -> outbox -> Celery -> LangGraph -> HITL -> reviewer decision path

## AI evaluation

Maintain a versioned golden dataset. Measure retrieval Recall@K/Precision@K/MRR, answer relevancy, faithfulness, citation precision/entailment, refusal correctness, freshness handling, latency and cost. Do not deploy a prompt/model/embedding change without regression comparison.
