# Runbooks

## Local startup
`docker compose up -d postgres redis`
`pip install -e '.[dev]'`
`alembic upgrade head`
`uvicorn app.main:app --reload`

## Celery worker
`celery -A app.workers.celery_app.celery_app worker -Q ingestion --loglevel=INFO`

## Common failure modes
- **Stale/absent prices**: fail closed; do not substitute fixture values. Check provider status and observed_at.
- **Vector query returns no results**: check tenant filter, embedding model/dimension, ingestion status, and index.
- **Graph stalls**: inspect thread ID/checkpoint, max execution time, node retry policy, and interrupt state.
- **Reviewer cannot decide**: verify reviewer/admin claim and review status; never bypass the workflow.
- **Duplicate ingestion**: verify idempotency key and unique source/version constraint.
- **Queue backlog**: inspect Celery queue depth, provider rate limits, worker concurrency, and retry storms.
