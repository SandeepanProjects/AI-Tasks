# Runbook

## API unavailable
1. Check `/health/live`.
2. Check `/health/ready`.
3. Inspect API logs using `X-Correlation-ID`.
4. Verify PostgreSQL and Redis health.

## Jobs stuck in queued
1. Verify Celery worker is running on queue `reviews`.
2. Check Redis connectivity.
3. Inspect `reviews.status` and worker logs.
4. Requeue only after confirming idempotent worker behavior.

## Failed workflow
Review `audit_events` and `workflow_checkpoints`. Do not manually edit approved records; use an authorized lifecycle transition.

## Database recovery
Use managed PostgreSQL backups/PITR in production. Test restoration regularly.
