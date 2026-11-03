# Operational runbook

## API unavailable
1. Check `/health/live` and `/health/ready`.
2. Inspect API logs using the `X-Correlation-ID` response header.
3. Verify PostgreSQL, Redis, migration service and network/DNS.
4. Check container restarts and resource limits.

## Jobs remain queued
1. Confirm Celery worker consumes `reviews,outbox` and Celery Beat is running.
2. Check Redis connectivity and queue depth.
3. Inspect `outbox_events` for `published_at`, `completed_at`, and `attempts`.
4. Check worker logs and tenant context propagation.
5. Pending outbox events are republished; processing is at-least-once, so keep handlers idempotent.

## Reviews remain running
1. Check `processing_started_at` and worker logs.
2. A running review has a ten-minute lease. An uncompleted outbox event is republished after the lease window; the worker can atomically reclaim a stale row.
3. Do not manually edit review status without recording an incident and corresponding audit event.

## Failed workflow
Inspect review status, audit events, checkpoints, model provider status, retrieval results, and correlation IDs. Distinguish provider/network failures from retrieval misses, guardrail rejections, and application defects. Retry only after identifying the cause. An administrator can use `POST /v1/reviews/{review_id}/retry`; this records a requeue audit event and writes a new outbox event atomically.

## Database recovery
Use managed PostgreSQL backups/PITR in production. Test restoration, migration rollback strategy, and RLS policies regularly.
