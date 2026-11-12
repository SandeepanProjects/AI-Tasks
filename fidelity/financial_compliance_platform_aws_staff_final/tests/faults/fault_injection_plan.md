# Fault-injection scenarios (staging only)

Run only against an isolated staging environment with synthetic tenant data.

1. **LLM provider timeout**: inject 20–30s latency and 5xx responses at the model gateway. Verify bounded timeout/retry, circuit-open behavior, visible degraded status, no duplicate review or approval.
2. **Redis/Celery outage**: stop Redis after outbox rows commit. Verify outbox remains pending, publisher retries, and tasks execute once logically after recovery.
3. **Worker termination**: kill a worker after graph checkpoint write but before task acknowledgement. Verify redelivery resumes the same thread and idempotency key.
4. **PostgreSQL failover**: restart the primary during a review. Verify transaction rollback, connection pool recovery and no partial audit/outbox write.
5. **Vector retrieval outage**: disable vector query path. Verify lexical fallback is marked in the result and alert/metric increments.
6. **Cross-tenant access**: replay tenant A evidence/document IDs under tenant B identity. Verify repository + RLS denial and security audit event.
7. **Load/soak**: execute Locust at 10, 50, 100 concurrent virtual users for 15 minutes each; capture p50/p95/p99, error rate, queue age, DB pool wait, tokens/request and cost/request. Set thresholds from an agreed SLO; do not treat this smoke test as a capacity certification.

Record build SHA, environment, injection window, expected/observed behavior and recovery time for every drill.
