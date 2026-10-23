# Production-grade LangGraph workflow recovery

In a production AI system, if a LangGraph workflow crashes halfway through execution, you generally want to resume from the last durable checkpoint instead of restarting the entire workflow.

For example, consider your enterprise financial advisor copilot:

1. Receive a user's financial question.
2. Retrieve relevant financial documents.
3. Analyze the portfolio.
4. Generate a recommendation.
5. Run a compliance check.
6. Wait for human approval.
7. Return the final response.

Suppose the application crashes after step 4. When the service restarts, you want LangGraph to recover the saved state and continue from the compliance check, without repeating expensive LLM calls or losing the portfolio analysis.

There are three important concepts:

- Checkpointing: Persist workflow state after graph execution steps.
- Recovery: Reopen the workflow using the same thread ID and checkpointer.
- Replay and idempotency: Safely handle operations that may execute again after a crash.

I'll show a complete, runnable reference implementation using Python, LangGraph, FastAPI, and PostgreSQL. It includes durable checkpoints, crash recovery, an API for resuming a workflow, and protection against unsafe repeated side effects.

One important distinction: LangGraph can resume from a saved checkpoint, but it cannot guarantee that every line of Python executes exactly once. If a process crashes during a node, that node may need to execute again. Production systems must account for that.

## 1. Download the complete project

LangGraph Workflow Recovery

Python · FastAPI · PostgreSQL · LangGraph

9 project files, including Docker Compose and setup instructions

Download the complete project ZIP

The project includes:

| File                 | Responsibility                                        |
| -------------------- | ----------------------------------------------------- |
| `app/state.py`       | Typed workflow state                                  |
| `app/graph.py`       | Graph nodes, edges and PostgreSQL checkpointer        |
| `app/api.py`         | Start, resume, inspect state and inspect history APIs |
| `requirements.txt`   | Python dependencies                                   |
| `docker-compose.yml` | Local PostgreSQL database                             |
| `Dockerfile`         | Container image                                       |
| `.env.example`       | Database configuration template                       |
| `README.md`          | Setup, API examples and recovery behavior             |

This is a runnable reference implementation with production-oriented structure. Before deploying it to a real financial-services environment, you must add actual authentication, tenant ownership enforcement, operational monitoring, and your real retrieval and LLM integrations.

## 2. The core recovery mechanism

The most important code is the PostgreSQL checkpointer. LangGraph uses it to persist graph state and retrieve it after a process restart. Unlike an in-memory checkpointer, PostgreSQL preserves checkpoints when the application process terminates.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub

+1



### `app/graph.py` — durable checkpointing

```
from psycopg.rows import dict_rowfrom psycopg_pool import ConnectionPoolfrom langgraph.checkpoint.postgres import PostgresSaverdef make_checkpointer(database_url: str):    pool = ConnectionPool(        conninfo=database_url,        min_size=1,        max_size=10,        timeout=10,        max_idle=300,        kwargs={            "autocommit": True,            "row_factory": dict_row,        },        open=False,    )    pool.open(wait=True)    checkpointer = PostgresSaver(pool)    checkpointer.setup()    return pool, checkpointer
```

Your graph must be compiled with this checkpointer:

```
graph = builder.compile(checkpointer=checkpointer)
```

Without that connection, your graph will not automatically persist its execution state to this database.

### Start a workflow with a stable ID

```
thread_id = "your-existing-workflow-uuid"config = {    "configurable": {        "thread_id": thread_id,    },    "recursion_limit": 25,}result = graph.invoke(    {        "request_id": "request-123",        "tenant_id": "tenant-456",        "question": "Analyze portfolio risk",    },    config=config,)
```

The `thread_id` identifies the workflow's persisted execution history. When recovering a workflow, you must reuse that same ID. Generating a new one starts a different workflow.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

GitHub

+1



## 3. Resume after a crash

Imagine this execution:

1\. Retrieve documents

Completed and checkpointed

2\. Analyze portfolio

Completed and checkpointed

3\. Compliance check

Application crashes during execution

PostgreSQL retains saved progress

The last committed checkpoint remains available

Restart and resume

Continue pending execution using the same thread ID

The recovery operation is straightforward:

```
config = {    "configurable": {        "thread_id": existing_thread_id,    },    "recursion_limit": 25,}# Read the checkpointed state.snapshot = graph.get_state(config)if not snapshot.values:    raise ValueError("No saved workflow state")# If there is no next node, the workflow may already be complete.if not snapshot.next:    result = snapshot.valueselse:    # Resume pending execution from the saved checkpoint.    result = graph.invoke(None, config=config)
```

The distinction between `graph.invoke(None, config=config)` and invoking the graph with a fresh input is important: the former continues the saved execution rather than starting a new workflow.

LangGraph also records successful writes from other nodes in a failed superstep, allowing those nodes to avoid unnecessary re-execution during recovery.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://langchain-ai.github.io\&sz=32)

Docs by LangChain

+1



## 4. How to run the project

Run these commands from the extracted project directory.

Step 1 — Start PostgreSQL

```
docker compose up -d postgres
```

Step 2 — Create the Python environment

```
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

Step 3 — Configure and start the API

```
cp .env.example .env
set -a
source .env
set +a

uvicorn app.api:app --reload
```

Step 4 — Start a workflow

```
curl -X POST http://localhost:8000/workflows \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Id: demo-tenant" \
  -d '{"question":"Analyze portfolio risk"}'
```

Copy the `thread_id` from the response.

Step 5 — Recover the workflow

After restarting the API process, use the same thread ID:

```
curl -X POST \
  http://localhost:8000/workflows/YOUR_THREAD_ID/resume \
  -H "X-Tenant-Id: demo-tenant"
```

The API implementation, including exception handling and state inspection, is in the downloadable project.

Important: `X-Tenant-Id` is a demonstration placeholder, not authentication. Do not expose this API to untrusted clients until you replace it with verified authentication and enforce thread ownership in your application database.

## 5. What if you need to resume from a specific historical checkpoint?

There are two different scenarios.

| Scenario                                                       | Correct approach                                               |
| -------------------------------------------------------------- | -------------------------------------------------------------- |
| Application crashed and you want to continue normal execution  | Reuse `thread_id` and resume from its latest saved checkpoint  |
| You want to inspect or replay an earlier point in the workflow | Select a historical `checkpoint_id`                            |
| You want to approve a human-in-the-loop interruption           | Resume using `Command(resume=approval_value)`                  |
| A node failed before its result was saved                      | Recover from the checkpoint; the failed node may execute again |

For a historical checkpoint, you can specify both IDs:

```
config = {    "configurable": {        "thread_id": existing_thread_id,        "checkpoint_id": historical_checkpoint_id,    }}historical_state = graph.get_state(config)
```

To continue from a historical point, you can invoke the graph with that configuration and suitable input. This is time travel or replay, not ordinary crash recovery; it can create a different execution path. Use it carefully in production, particularly if subsequent nodes perform external actions.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://reference.langchain.com\&sz=32)

LangChain Reference

+1



## 6. Production safeguards you should not skip

The reference project provides the persistence foundation, but a production-grade recovery system also needs these safeguards.

- Idempotency: A payment, trade, email or external API call must not execute twice merely because its node was retried. Use stable operation IDs and enforce uniqueness in the external system or your database.
- Automatic recovery: PostgreSQL preserves checkpoints, but it does not automatically restart abandoned workflows. Use a durable job table or queue, a worker, bounded retries and a recovery scheduler.
- State validation: Validate saved state and external references before executing sensitive nodes.
- Timeouts and retries: Configure bounded retries for transient LLM, vector database and network failures. Do not retry permanent errors indefinitely.
- Observability: Track `thread_id`, node name, checkpoint ID, retry count, error category, latency and token cost.
- Security: Enforce tenant authorization for every workflow operation. Keep secrets and large documents out of checkpoint state.
- Deployment migrations: Run checkpoint database setup and migrations as a controlled deployment task when operating multiple replicas.

One final detail matters at staff-engineer level: a checkpoint is not a transaction covering every external side effect. If a node successfully charges a payment provider but crashes before saving its result, the node may execute again. The robust solution is an idempotent external operation or a transactional outbox—not simply adding more checkpoints.

The complete downloadable project gives you the core workflow, durable persistence, recovery endpoints and local setup. The remaining work is to integrate your actual AI agents and production security and operations infrastructure.