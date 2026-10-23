# Durable LangGraph HITL reference

Python + FastAPI + LangGraph + PostgreSQL checkpointer. It demonstrates a draft -> human approval interrupt -> publish/reject graph, persistent checkpointing, state inspection, approval audit rows, and crash recovery.

## Run locally

Requires Docker and Python 3.12+.

```bash
docker compose up -d postgres
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
set -a && source .env && set +a
uvicorn app.api:app --reload
```

Browse `http://localhost:8000/docs`.

## Start a workflow

The example uses headers as placeholders only:

```bash
curl -X POST http://localhost:8000/workflows   -H 'Content-Type: application/json'   -H 'X-Tenant-Id: demo-tenant'   -H 'X-Reviewer-Id: reviewer-123'   -d '{"question":"Review this portfolio recommendation"}'
```

The response returns `thread_id`, `status=awaiting_approval`, and the interrupt payload with `approval_id`.

## Inspect the paused workflow

```bash
curl http://localhost:8000/workflows/THREAD_UUID   -H 'X-Tenant-Id: demo-tenant'   -H 'X-Reviewer-Id: reviewer-123'
```

## Approve or reject

```bash
curl -X POST http://localhost:8000/workflows/THREAD_UUID/approve   -H 'Content-Type: application/json'   -H 'X-Tenant-Id: demo-tenant'   -H 'X-Reviewer-Id: reviewer-123'   -d '{"approval_id":"COPY_APPROVAL_ID","decision":"approve","comment":"Reviewed"}'
```

Use `decision: "reject"` to reject.

## Crash recovery

- A paused approval survives process restarts because its graph state is checkpointed in PostgreSQL.
- After a crash, call `GET /workflows/{thread_id}` to inspect state.
- If a normal graph node failed and no interrupt is pending, call `POST /workflows/{thread_id}/recover`.
- If an interrupt is pending, submit the recorded decision to `/approve`. Do not treat crash recovery as approval.
- Always reuse the same `thread_id`; do not start a new workflow to recover an old one.

## Important production work still required

This is a production-oriented reference, not a claim of being ready to deploy unchanged. Replace header-based identity with verified JWT/OIDC auth, implement reviewer RBAC and segregation of duties, run checkpoint setup as a controlled migration, add rate limiting, structured metrics/tracing, request-level idempotency, a durable worker/outbox for reconciling approval audit and graph resume, and idempotency keys for external side effects.

LangGraph restarts the node containing `interrupt()` from the beginning when resumed. Keep side effects out of code before `interrupt()`. An external side effect may occur even if the process crashes before the graph checkpoint is committed, so use an idempotent downstream API or transactional outbox.

## 8. The most important production behavior

1. Workflow pauses: `interrupt()` exposes the proposed action and persists the graph checkpoint.
2. Human decides: The API authenticates the reviewer, validates the decision and records the approval audit.
3. Workflow resumes: `graph.invoke(Command(resume=decision), config=config)` resumes the existing thread.
4. Crash occurs: Reuse the same `thread_id`, inspect the checkpoint and recover without automatically approving anything.
5. External action executes: Use a durable idempotency key or transactional outbox so retries do not accidentally perform an action twice.

These behaviors follow LangGraph's documented interrupt and persistence model.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub

+2



A production caveat: There is no single exact codebase used by every production company. The project is a runnable, production-oriented reference, not a certified deployment-ready financial platform. In particular, replace its demonstration authentication headers, add robust approval-to-workflow reconciliation, and test crash scenarios before deploying it.

For your financial advisor or compliance copilot, I would put HITL before releasing a recommendation, approving a compliance-sensitive communication, or executing any consequential financial action.