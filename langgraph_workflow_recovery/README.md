# LangGraph durable workflow recovery

Reference implementation: FastAPI + LangGraph + PostgreSQL checkpointer.

## What it demonstrates

- PostgreSQL-backed durable checkpoints (not in-memory state).
- A stable `thread_id` for each workflow.
- Resume a failed/incomplete workflow using `graph.invoke(None, config=...)`.
- Inspect current state and checkpoint history.
- Bounded graph execution via `recursion_limit`.
- A basic API shape and a clear placeholder for authentication/tenant authorization.

This is a production-oriented reference, not a drop-in production service. Before deploying, implement real authentication and authorization, workflow ownership in your application database, request idempotency, rate limiting, migrations/backup policy, metrics/tracing, and node-level timeouts/retries.

## Run locally

Requires Python 3.12+ and Docker.

```bash
docker compose up -d postgres
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
set -a && source .env && set +a
uvicorn app.api:app --reload
```

Open `http://localhost:8000/docs`.

For each request below, send the `X-Tenant-Id` header. It is only a demo placeholder and is NOT authentication.

## Start workflow

```bash
curl -X POST http://localhost:8000/workflows \
  -H 'Content-Type: application/json' \
  -H 'X-Tenant-Id: demo-tenant' \
  -d '{"question":"Summarize the portfolio risk factors"}'
```

Copy the returned `thread_id`. If execution completes, it returns `completed`. If a node raises an exception, it returns `failed_recoverable` and the saved checkpoints remain in PostgreSQL.

## Resume after restart/crash

Restart the API process, then call:

```bash
curl -X POST http://localhost:8000/workflows/THREAD_UUID/resume \
  -H 'X-Tenant-Id: demo-tenant'
```

The resume endpoint reuses the exact same `thread_id` and calls `graph.invoke(None, config=...)`. Do not generate a new thread ID for recovery.

## Inspect saved state

```bash
curl http://localhost:8000/workflows/THREAD_UUID/state \
  -H 'X-Tenant-Id: demo-tenant'
```

## Inspect checkpoint history

```bash
curl 'http://localhost:8000/workflows/THREAD_UUID/history?limit=20' \
  -H 'X-Tenant-Id: demo-tenant'
```

## Crash semantics and important caveats

1. LangGraph checkpoints graph state at execution boundaries (supersteps). It does not persist arbitrary local Python variables mid-node.
2. If a node completed and its output was checkpointed, recovery can continue from that saved progress.
3. If a process dies while a node is executing before its output is committed, the node can execute again. External side effects must therefore be idempotent.
4. For an explicit human pause (`interrupt()`), resume with `graph.invoke(Command(resume=approved_value), config)`; this differs from retrying a failed node.
5. To inspect/fork from a specific historical checkpoint, pass its `checkpoint_id` along with `thread_id`. This is time-travel/replay and can create a new branch of execution; it is not the default crash-recovery strategy. Do not overwrite production business state when experimenting with historical checkpoints.
6. Do not put secrets, huge PDFs, full source documents, or unrestricted customer data into graph state. Store large data externally and checkpoint stable IDs/references.
7. Use a durable application-level job table/outbox if a workflow must be automatically retried by a worker after a pod dies. A process restart alone does not guarantee the API will automatically resume every abandoned workflow.
8. The demo `X-Tenant-Id` header is not secure. Replace it with verified identity and enforce ownership for every read/resume endpoint.
9. `checkpointer.setup()` is shown for a small self-managed deployment. In mature environments, run database migrations as a controlled deployment step rather than racing multiple API replicas on startup.
