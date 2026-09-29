# Financial Compliance Multi-Agent Platform — Complete Architecture and Step-by-Step Explanation

This project is designed to review financial marketing material, investment-product descriptions, and advisor communications against an approved set of compliance policies.

The central idea is:

> A user submits financial content → multiple specialized agents analyze it → tools retrieve relevant policies → the system produces a traceable risk assessment → a human reviewer makes the final decision.

I'll explain it from the beginning: the business objective, architecture, folder structure, database, RAG pipeline, each agent and tool, both execution flows, sample inputs and outputs, and how the entire system connects.

# 1. What problem does this application solve?

Imagine a financial company is preparing this marketing statement:

> “Our investment product guarantees 15% annual returns with absolutely no risk.”

Before publishing it, the company wants to check whether the statement conflicts with its approved policies.

A manual compliance reviewer would need to:

1. Read the marketing statement.

2. Identify the claims being made.

3. Search internal compliance policies.

4. Compare each claim against those policies.

5. Determine whether the claim needs investigation.

6. Record the evidence and findings.

7. Approve, reject, or escalate the content.

8. Keep an audit trail.

This application automates much of that preliminary investigation.

## The expected result

High risk

Pending human approval

## Preliminary compliance review

Submitted statement

“Our investment product guarantees 15% annual returns with absolutely no risk.”

Potential issues identified

* Guaranteed-return language requires substantiation and policy review.

* The statement claims there is no investment risk.

* Relevant performance and risk-disclosure policies should be examined.

  Recommended action: Block publication pending compliance review.

  Illustrative result. The included fallback analyzer uses simple rules; a model-enabled run may produce different findings. A real compliance decision requires an authorized human.

The system is a decision-support application, not an autonomous legal or regulatory authority.

# 2. Entire architecture at a glance

First, understand the major components and what each one is responsible for.

User / Compliance Reviewer

Submits content, checks findings, makes decisions

FastAPI — HTTP API

Request validation, authentication, role checks

Review Service

Creates reviews, runs workflows, saves decisions

## LangGraph workflow

1. Claim Extraction Agent

2. Policy Research Agent

3. Compliance Analysis Agent

4. Risk Assessment Agent

5. Guardrails

PostgreSQL + pgvector

Policies, reviews, embeddings, audit records

Redis + Celery

Caching and background review jobs

Human decision

Approve or reject → persist decision and audit event

The actual LangGraph workflow is defined in `app/graph/workflow.py`. It connects five nodes in a fixed sequence, from claim extraction through guardrail validation.

There are two execution options:

* Synchronous: FastAPI waits while the workflow runs.

* Asynchronous: FastAPI queues a Celery job, and a separate worker runs the workflow.

Both options ultimately use the same review service and agent workflow.

# 3. Understand the folder structure first

The application is organized into layers. Each layer has a specific responsibility.

```
financial_compliance_multi_agent/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   └── routes/
│   │       ├── reviews.py
│   │       ├── policies.py
│   │       └── health.py
│   │
│   ├── auth/
│   │   └── dependencies.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   │
│   ├── models/
│   │   ├── policy.py
│   │   ├── review.py
│   │   └── audit.py
│   │
│   ├── schemas/
│   │   ├── policy.py
│   │   ├── review.py
│   │   └── agent.py
│   │
│   ├── rag/
│   │   ├── ingestion.py
│   │   ├── embeddings.py
│   │   └── retriever.py
│   │
│   ├── tools/
│   │   ├── policy_search.py
│   │   ├── policy_lookup.py
│   │   └── claim_evidence.py
│   │
│   ├── agents/
│   │   ├── base.py
│   │   ├── claim_extraction.py
│   │   ├── policy_research.py
│   │   ├── compliance_analysis.py
│   │   └── risk_assessment.py
│   │
│   ├── graph/
│   │   ├── state.py
│   │   └── workflow.py
│   │
│   ├── guardrails/
│   │   └── output_validation.py
│   │
│   ├── services/
│   │   └── review_service.py
│   │
│   ├── cache/
│   │   └── redis_client.py
│   │
│   └── worker/
│       ├── celery_app.py
│       └── tasks.py
│
├── data/
│   ├── policies/
│   └── eval/
│
├── tests/
├── migrations/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## What each layer means

|
Layer

|

Responsibility

|
| --- | --- |
|

`api`

|

Receives HTTP requests and returns responses

|
|

`auth`

|

Identifies the caller and checks their role

|
|

`services`

|

Implements the review lifecycle

|
|

`agents`

|

Performs individual analysis tasks

|
|

`tools`

|

Provides bounded capabilities to retrieve information

|
|

`rag`

|

Ingests policies, creates embeddings, retrieves relevant text

|
|

`graph`

|

Orchestrates the agents in the correct order

|
|

`guardrails`

|

Validates the generated result and its citations

|
|

`models`

|

Defines database tables

|
|

`schemas`

|

Defines request, response, and agent data structures

|
|

`cache`

|

Stores reusable retrieval results in Redis

|
|

`worker`

|

Runs long-running jobs outside the API process

|

Important distinction: an agent reasons about a task; a tool performs a specific operation. For example, the Policy Research Agent decides what information it needs, while `search_policies()` actually queries the policy database.

# 4. Step one — Start the application

The entry point is:

`app/main.py`

When the application starts, FastAPI executes its lifespan setup.

In this project, that setup:

1. Opens a connection to PostgreSQL.

2. Enables the PostgreSQL `vector` extension.

3. Creates the tables declared by the SQLAlchemy models, if they do not exist.

4. Starts serving HTTP requests.

5. Disposes of the database engine during shutdown.

The relevant setup is in `app/main.py`.

The app registers three route groups:

* `/health`

* `/api/v1/policies`

* `/api/v1/reviews`

When you run:

Bash

```
docker compose up --build
```

Docker Compose starts the PostgreSQL, Redis, API, and Celery worker services. The API and worker use the same application code and configuration, but they run as separate processes.

## What is Docker doing here?

Think of Docker Compose as starting the application's supporting services together.

API container

Port 8000

PostgreSQL + pgvector

Port 5432

Redis

Port 6379

Celery worker

Background jobs

Redis is used both as a cache and as the Celery broker/result backend, with different Redis database numbers configured in `.env.example`.

# 5. Step two — Configure the application

The configuration is in `app/core/config.py`, with example environment variables in `.env.example`.

Important settings include:

dotenv

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/compliance
REDIS_URL=redis://redis:6379/0

CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
```

### What these settings control

* `DATABASE_URL`: where SQLAlchemy connects to PostgreSQL.

* `REDIS_URL`: where the retrieval cache lives.

* `CELERY_BROKER_URL`: where queued jobs are placed.

* `OPENAI_API_KEY`: enables model-based claim extraction, analysis, and embeddings.

* `OPENAI_MODEL`: the configured chat model.

* `EMBEDDING_MODEL`: the model used to embed policy text and search queries.

If the OpenAI key is absent, the application uses deterministic fallback logic for the agents and keyword retrieval instead of semantic vector retrieval. That fallback is useful for local demonstrations, but it is not equivalent to an LLM-based compliance analysis.

# 6. Step three — Understand the database

The project defines three primary database models.

## 6.1 `PolicyChunk`

File: `app/models/policy.py`

Stores policy text that can be searched.

Conceptually:

|
Field

|

Meaning

|
| --- | --- |
|

`id`

|

Unique database ID for this chunk

|
|

`tenant_id`

|

Which tenant owns the policy

|
|

`policy_code`

|

Policy identifier, such as `RISK-002`

|
|

`title`

|

Policy title

|
|

`text`

|

Actual policy text

|
|

`embedding`

|

Vector representation of the text

|
|

`created_at`

|

Creation timestamp

|

A long policy can be split into multiple chunks. Each chunk gets its own database ID and embedding.

## 6.2 `Review`

File: `app/models/review.py`

Stores each submitted compliance review.

|
Field

|

Meaning

|
| --- | --- |
|

`id`

|

Review UUID

|
|

`tenant_id`

|

Tenant that owns the review

|
|

`submitted_by`

|

User who submitted it

|
|

`content`

|

Original submitted statement

|
|

`status`

|

Current lifecycle state

|
|

`result`

|

Structured findings and risk result

|
|

`decided_by`

|

Human decision-maker

|
|

`decision_comment`

|

Approval/rejection explanation

|

## 6.3 `AuditEvent`

File: `app/models/audit.py`

Records important actions, such as:

* Review created

* Analysis completed

* Analysis failed

* Review approved

* Review rejected

This is important because a compliance system should be able to explain who did what and when.

The current audit table is an application-level audit log. For regulated production use, you would also want stronger tamper-resistance, retention controls, and possibly immutable external audit storage.

# 7. Step four — Load the compliance policies

Before reviewing a statement, the system needs policies to compare it against.

The project includes a seed endpoint that creates three sample policies.

## Sample policy library

ADV-001

Performance claims

Past performance does not guarantee future results. Performance claims must be accurate, balanced, and supported.

RISK-002

Risk disclosure

Do not describe investments as risk-free or guaranteed unless an approved guarantee applies. Disclose material risks.

FEES-003

Fees and costs

Fees, expenses, and material costs must be disclosed clearly and not obscured.

These are synthetic demonstration policies, not legal advice or a complete regulatory rulebook.

## How to seed them

After starting the application, call:

Bash

```
curl -X POST http://localhost:8000/api/v1/policies/seed \
  -H "Authorization: Bearer demo-admin"
```

The endpoint checks whether each policy code already exists for the current tenant. If not, it sends the policy text to the ingestion function.

The seed endpoint and its sample policies are defined in `app/api/routes/policies.py`.

## What happens during ingestion?

The call chain is:

```
POST /api/v1/policies/seed
        |
        v
policies.py
        |
        v
ingest_policy()
        |
        +--> Split text into paragraphs/chunks
        |
        +--> Generate embedding, if OpenAI is configured
        |
        +--> Save chunks in PostgreSQL
```

The `ingest_policy()` function splits the input on blank lines. It generates an embedding for each chunk when an OpenAI client is configured, then stores the chunk and its vector in PostgreSQL.

Why embeddings? They allow the application to find policy text that is semantically related to a query, even when the wording differs.

For example, a search for “investments with no downside” could retrieve a policy discussing “risk-free investments,” even though those phrases are not identical.

The current chunker is intentionally simple. A production ingestion pipeline should also preserve document version, source location, effective date, jurisdiction, and approval status.

# 8. Step five — Understand RAG in this project

RAG means Retrieval-Augmented Generation.

Instead of asking an LLM to answer a compliance question using only its pretrained knowledge, the application retrieves relevant approved policy text and supplies it as context.

The flow is:

Query

“Can we promise a guaranteed return?”

Embedding / keyword search

Convert query to a vector, if configured

PostgreSQL + pgvector

Retrieve relevant tenant-specific policy chunks

Evidence

Policy IDs, codes, titles, and excerpts

## 8.1 Embedding service

File: `app/rag/embeddings.py`

The `EmbeddingService` calls the configured OpenAI embedding model.

It is used both when ingesting policies and when searching for relevant policies.

If no OpenAI key is configured, the service returns no vector. The retriever then falls back to keyword matching.

## 8.2 Retriever

File: `app/rag/retriever.py`

The `PolicyRetriever.search()` function does four important things:

1. Builds a cache key that includes the tenant and query.

2. Checks Redis for a cached result.

3. If not cached, searches PostgreSQL using vector similarity or keyword matching.

4. Stores the results in Redis and returns them.

The database query is scoped to the current tenant, so the search is not intended to return another tenant's policies.

### Semantic search vs keyword fallback

|
Mode

|

How it finds policies

|
| --- | --- |
|

Semantic

|

Compares query embedding with stored policy embeddings using cosine distance

|
|

Keyword fallback

|

Searches for matching words in policy text

|

Semantic search requires actual stored embeddings. If you seed policies without an OpenAI key, those rows will have no embeddings and the app uses keyword search.

# 9. Step six — Understand the tools

The project contains three explicit tools.

## Tool 1: `search_policies`

File: `app/tools/policy_search.py`

Purpose: search for policy chunks relevant to a claim.

Example:

Python

Run

```
records = await search_policies(
    db=db,
    tenant_id="demo",
    query="guaranteed investment returns",
    limit=5,
)
```

The tool delegates to `PolicyRetriever`.

It returns policy records with fields such as:

JSON

```
[
  {
    "policy_id": 2,
    "policy_code": "RISK-002",
    "title": "Risk disclosure",
    "text": "Do not describe investments as risk-free..."
  }
]
```

The exact IDs depend on the database.

## Tool 2: `get_policy_by_code`

File: `app/tools/policy_lookup.py`

Purpose: retrieve policy chunks by an exact policy code.

Example:

Python

Run

```
records = await get_policy_by_code(
    db=db,
    tenant_id="demo",
    policy_code="RISK-002",
)
```

This is useful when another part of the workflow already knows which policy it needs.

Current implementation detail: the tool is defined and available in the codebase, but the current `PolicyResearchAgent.run()` does not call it. The research agent currently uses `search_policies()` and `extract_claim_evidence()`.

## Tool 3: `extract_claim_evidence`

File: `app/tools/claim_evidence.py`

Purpose: package retrieved policy records into bounded evidence excerpts associated with a claim.

It returns information such as:

JSON

```
{
  "policy_id": 2,
  "policy_code": "RISK-002",
  "title": "Risk disclosure",
  "excerpt": "Do not describe investments as risk-free...",
  "term_overlap": 1
}
```

The overlap value is a simple lexical signal, not a legal or semantic relevance score.

## Why not let an LLM run arbitrary code?

The tools are ordinary application functions. The workflow controls when they run and passes the tenant ID from the authenticated request context.

That is deliberate: database access, tenant scoping, and allowed operations should be controlled by the application rather than by arbitrary model-generated code.

# 10. Step seven — Understand each agent

Now we reach the multi-agent part.

The project has four specialized agents. They are not four independent services or four separate servers. They are components invoked by the LangGraph workflow.

## Agent 1: Claim Extraction Agent

File: `app/agents/claim_extraction.py`

### Responsibility

Extract the material claims from the submitted text.

### Sample input

```
Our investment product guarantees 15% annual returns
with absolutely no risk.
```

### Possible model output

JSON

```
{
  "claims": [
    {
      "text": "Our investment product guarantees 15% annual returns",
      "claim_type": "performance_guarantee"
    },
    {
      "text": "Our investment product has absolutely no risk",
      "claim_type": "risk_claim"
    }
  ]
}
```

This is an illustrative model response, not a guaranteed output.

The agent asks the configured chat model to return JSON. If no model is configured, its fallback treats the entire submitted statement as one claim.

That distinction matters: the fallback does not perform sophisticated claim segmentation.

Why do we extract claims separately? Because a long financial document may contain dozens of distinct statements, and each may need different policy evidence.

## Agent 2: Policy Research Agent

File: `app/agents/policy_research.py`

### Responsibility

Find the policies relevant to each extracted claim and organize evidence.

It calls:

```
PolicyResearchAgent
      |
      +--> search_policies()
      |        |
      |        +--> Redis
      |        +--> PostgreSQL / pgvector
      |
      +--> extract_claim_evidence()
```

For the claim:

> “Our investment product guarantees 15% annual returns.”

The search may retrieve:

* `ADV-001` — Performance claims

* `RISK-002` — Risk disclosure

It then associates the retrieved excerpts with the claim.

The result contains:

* `evidence_by_claim`: evidence grouped by claim

* `policies`: deduplicated retrieved policy records

* `tools_used`: names of the tools used

This agent does not make the final compliance decision. Its job is to gather relevant evidence.

## Agent 3: Compliance Analysis Agent

File: `app/agents/compliance_analysis.py`

### Responsibility

Compare each claim with the supplied policy evidence.

It receives a context containing:

JSON

```
{
  "content": "Our investment product guarantees 15% annual returns with absolutely no risk.",
  "claims": [
    {
      "text": "Our investment product guarantees 15% annual returns",
      "claim_type": "performance_guarantee"
    }
  ],
  "evidence": [
    {
      "claim": "Our investment product guarantees 15% annual returns",
      "evidence": [
        {
          "policy_id": 2,
          "policy_code": "RISK-002",
          "excerpt": "Do not describe investments as risk-free..."
        }
      ]
    }
  ]
}
```

The agent is instructed to return structured findings and not invent policy IDs.

A finding may have one of these statuses:

|
Status

|

Meaning

|
| --- | --- |
|

`potential_violation`

|

A possible policy conflict was identified

|
|

`compliant`

|

The available evidence supports compliance

|
|

`needs_review`

|

More investigation is needed

|
|

`insufficient_evidence`

|

The retrieved material does not provide enough evidence

|

The actual model output depends on the model, prompt, and retrieved evidence.

### What happens without an API key?

The fallback looks for terms such as `guarantee`, `guaranteed`, `no risk`, `risk-free`, and `certain return`.

If it detects one, it marks the claim as `potential_violation`. Otherwise, it uses the evidence availability to decide between `needs_review` and `insufficient_evidence`.

That is a deliberately basic demonstration heuristic, not a complete compliance reasoning engine.

## Agent 4: Risk Assessment Agent

File: `app/agents/risk_assessment.py`

### Responsibility

Translate finding statuses into risk levels and an overall recommended action.

The current mapping is:

|
Finding status

|

Assigned risk

|
| --- | --- |
|

`potential_violation`

|

High

|
|

`insufficient_evidence`

|

Medium

|
|

`compliant`

|

Low

|
|

`needs_review`

|

Medium

|

The agent then selects the highest risk across all findings.

For example:

JSON

```
{
  "overall_risk": "high",
  "recommended_action": "block_and_escalate"
}
```

The risk rubric is a simple, fixed mapping. It is not a calibrated financial-risk model, and the thresholds should be approved by the compliance team before production use.

# 11. Step eight — How LangGraph orchestrates the agents

File: `app/graph/workflow.py`

LangGraph is the orchestration layer. It controls which node runs next and carries shared state between nodes.

The current graph is linear:

```
START
  |
  v
extract_claims
  |
  v
research_policies
  |
  v
analyze
  |
  v
risk
  |
  v
guardrails
  |
  v
END
```

There are no conditional branches or retry loops in this version.

## What is graph state?

File: `app/graph/state.py`

The state is a shared data structure containing values such as:

Python

Run

```
{
    "review_id": "...",
    "tenant_id": "demo",
    "content": "...",
    "claims": [],
    "research": {},
    "analysis": {},
    "result": {}
}
```

Each node reads the values it needs and returns updates.

For example:

Python

Run

```
async def extract_claims(state):
    claims = await claim_agent.run(state["content"])
    return {"claims": claims}
```

LangGraph merges that update into the workflow state. The next node can then read `state["claims"]`.

### Why use LangGraph rather than calling functions manually?

For this current, small workflow, ordinary Python function calls could work too.

LangGraph becomes more useful as the application grows to include:

* Conditional routing

* Retry and fallback paths

* Parallel agents

* Human checkpoints

* Durable execution

* Complex state transitions

The present project establishes the graph structure, but does not yet implement all those advanced features.

# 12. Step nine — Guardrails validate the result

File: `app/guardrails/output_validation.py`

After risk assessment, the workflow validates the result before persisting it.

There are two main checks.

## Check 1: Is the output structurally valid?

The result is validated using the Pydantic `ReviewResult` schema.

It expects fields such as:

JSON

```
{
  "summary": "...",
  "claims": [],
  "findings": [],
  "overall_risk": "high",
  "recommended_action": "block_and_escalate"
}
```

This helps prevent malformed agent output from silently entering the database.

## Check 2: Are cited policy IDs legitimate?

The workflow collects the IDs of policies retrieved during the research stage.

For each finding, it checks that every cited policy ID belongs to that set.

Conceptually:

Python

Run

```
allowed_policy_ids = {
    policy["policy_id"]
    for policy in retrieved_policies
}

for finding in findings:
    for policy_id in finding["policy_ids"]:
        if policy_id not in allowed_policy_ids:
            raise ValueError("Unknown policy citation")
```

If the model invents an ID that was never retrieved, validation fails and the review is marked failed by the review service.

This is a citation provenance check. It proves that the ID came from the retrieved set; it does not prove that the policy was interpreted correctly or that the citation fully supports the claim.

The code validates the output schema and policy-ID provenance before marking citations as validated.

# 13. Step ten — Full sample input, from API to result

Let's walk through an actual end-to-end scenario.

## First: create a review

Request:

http

```
POST /api/v1/reviews
Authorization: Bearer demo-reviewer
Content-Type: application/json
```

Body:

JSON

```
{
  "tenant_id": "demo",
  "content": "Our investment product guarantees 15% annual returns with absolutely no risk."
}
```

The route uses the authenticated principal's tenant ID. In this demo, the token maps to the `demo` tenant.

The review service creates a database record with a UUID and sets:

JSON

```
{
  "status": "queued"
}
```

It also records a `review_created` audit event.

Important: the request's `tenant_id` is not used to select the tenant. The service uses the authenticated principal's tenant, which is the correct general pattern for preventing users from choosing arbitrary tenant IDs.

## Second: run the review

Request:

http

```
POST /api/v1/reviews/REVIEW_ID/run
Authorization: Bearer demo-reviewer
```

The route checks that the review is in `queued` or `failed` status, then calls `ReviewService.run()`.

The service changes the status to `processing` and invokes the LangGraph workflow.

## Third: agents execute

The graph processes the text:

1. Claim Extraction Agent identifies the claims.

2. Policy Research Agent searches the policy library.

3. Compliance Analysis Agent compares claims with evidence.

4. Risk Assessment Agent assigns risk levels.

5. Guardrails validate the result.

## Fourth: result is saved

If the workflow succeeds, the review is stored with:

JSON

```
{
  "status": "pending_approval",
  "result": {
    "summary": "Preliminary automated review; human approval required.",
    "overall_risk": "high",
    "recommended_action": "block_and_escalate",
    "citations_validated": true
  }
}
```

This abbreviated result illustrates the fallback behavior. A real response contains claims, findings, policy IDs, policy codes, and other metadata.

The service persists the result and records an `analysis_completed` audit event.

## Fifth: retrieve the review

http

```
GET /api/v1/reviews/REVIEW_ID
Authorization: Bearer demo-reviewer
```

The response includes the review's current status and stored analysis.

## Sixth: a human decides

An authorized approver can send:

http

```
POST /api/v1/reviews/REVIEW_ID/decision
Authorization: Bearer demo-approver
Content-Type: application/json
```

JSON

```
{
  "decision": "rejected",
  "comment": "The guaranteed-return and no-risk claims need substantiation and compliance review."
}
```

The service:

1. Checks that the review is `pending_approval`.

2. Changes its status to `rejected`.

3. Stores the approver's identity and comment.

4. Creates a `review_rejected` audit event.

The decision endpoint only permits a decision while the review is pending approval.

# 14. The review lifecycle

The status of a review changes as it moves through the application.

queued

Review submitted

processing

Workflow and agents are running

pending_approval

Analysis saved; waiting for a human

approved

Human approves

rejected

Human rejects

If analysis fails, the status becomes `failed`.

This is application-level human-in-the-loop (HITL). The workflow itself does not pause at a LangGraph `interrupt()` checkpoint and resume later. Instead, the graph finishes, its result is saved, and the separate API decision endpoint records the human decision.

That is a valid simple approval pattern, but it is different from durable graph-level HITL.

# 15. Synchronous flow vs asynchronous flow

This is one of the most important architecture concepts.

## Option A: synchronous execution

```
Client
  |
  v
FastAPI /reviews/{id}/run
  |
  v
ReviewService.run()
  |
  v
LangGraph + agents + RAG
  |
  v
Save result to PostgreSQL
  |
  v
HTTP response
```

The HTTP request remains open while the analysis runs.

Use this for local testing, demos, and short-running tasks.

## Option B: asynchronous execution with Celery

```
Client
  |
  v
FastAPI /reviews/{id}/enqueue
  |
  v
Redis broker
  |
  v
Celery worker
  |
  v
ReviewService.run()
  |
  v
LangGraph + agents + RAG
  |
  v
PostgreSQL updated
```

The API returns a task ID after enqueuing the job. The worker then loads the review from PostgreSQL and executes the same review service.

The task implementation uses `asyncio.run()` to execute the async workflow inside the synchronous Celery task.

### Why do we need Celery?

Suppose an organization submits 500 documents for review.

If every HTTP request holds a connection open while an LLM analyzes the document, the API can become overloaded.

With Celery:

* API requests can return quickly.

* Jobs wait in a queue.

* Workers process jobs separately.

* You can scale the number of workers independently of the API.

For a production system, also add job idempotency, retries, queue monitoring, rate limits, and protection against duplicate concurrent processing.

# 16. Where Redis fits in the application

Redis has two distinct uses.

## Use 1: retrieval caching

When a policy search is performed, the retriever checks Redis first.

```
Policy search
    |
    v
Redis cache hit?
   / \
 Yes  No
  |    |
Return  Query PostgreSQL
        |
        v
     Cache result
        |
        v
     Return result
```

This can reduce repeated database work for identical queries.

The cache key includes the tenant, which helps keep tenants' cached results separate.

One caveat: the current cache key does not include a policy-library version. If a policy is updated, an old cached result may remain until the TTL expires. A production implementation should invalidate relevant entries or include a policy version in the key.

## Use 2: Celery message broker

Redis also carries queued job messages from the API to the worker.

That is separate from retrieval caching, even though both use Redis.

# 17. Authentication and authorization

File: `app/auth/dependencies.py`

The demo has three tokens:

|
Token

|

Role

|

Example permissions

|
| --- | --- | --- |
|

`demo-admin`

|

Admin

|

Manage policies; access reviews

|
|

`demo-reviewer`

|

Reviewer

|

Submit and run reviews

|
|

`demo-approver`

|

Approver

|

Review findings and make decisions

|

The `require_roles()` dependency checks the principal's role before the route proceeds.

For example:

Python

Run

```
user = Depends(require_roles("admin", "approver"))
```

means only users with either role may call that route.

This is demo authentication only. The tokens are hard-coded, and the principal data is not derived from a verified JWT. Do not expose these demo tokens in a deployed environment. Replace this adapter with real OIDC/JWT verification, proper role claims, and tenant authorization.

# 18. What happens when something fails?

The main failure cases include:

|
Failure

|

Current behavior

|
| --- | --- |
|

Invalid/missing bearer token

|

API returns 401

|
|

Insufficient role

|

API returns 403

|
|

Review not found in caller's tenant

|

API returns 404

|
|

Review in an invalid lifecycle state

|

API returns 409

|
|

Agent or retrieval error

|

Review becomes `failed`

|
|

Invalid agent schema

|

Guardrails raise an error

|
|

Citation references an un-retrieved policy ID

|

Guardrails reject the result

|
|

OpenAI key missing

|

Deterministic fallback and keyword search

|

The current workflow does not have a graph-level retry node or provider fallback. Those are sensible next steps for a production implementation.

# 19. Tests and evaluation

The project includes:

* `tests/test_risk_assessment.py`

* `tests/test_guardrails.py`

* `data/eval/reviews.jsonl`

The risk-assessment tests check the mapping from a potential violation to high risk, and the default behavior for empty findings.

The guardrail test checks that an unknown policy citation is rejected.

The JSONL evaluation file contains sample inputs and expected risk labels. It is a small evaluation dataset, not a full evaluation runner or a statistically meaningful benchmark.

Run the unit tests from the project directory:

Bash

```
pytest -q
```

For a serious compliance application, expand evaluation to cover:

* Claim extraction precision and recall

* Retrieval recall@k and ranking quality

* Citation correctness

* False positives and false negatives

* Risk classification agreement with compliance reviewers

* Prompt injection and malicious document content

* Regression tests across model or prompt changes

# 20. A complete call trace: who calls whom?

Here is the whole application in one sequence.

1. `app/main.py`

   Starts FastAPI, initializes database tables, registers routers.

2. `app/api/routes/reviews.py`

   Receives the review request, validates input, checks the caller's role, and invokes the service.

3. `app/services/review_service.py`

   Creates the review record, changes lifecycle status, calls the graph, and persists results.

4. `app/graph/workflow.py`

   Invokes the nodes in order and passes shared state between them.

5. `app/agents/claim_extraction.py`

   Extracts the claims.

6. `app/agents/policy_research.py`

   Calls policy search and evidence extraction tools.

7. `app/rag/retriever.py`

   Checks Redis, then searches PostgreSQL/pgvector or uses keyword matching.

8. `app/agents/compliance_analysis.py`

   Compares claims with retrieved policy evidence.

9. `app/agents/risk_assessment.py`

   Assigns risk and recommends an action.

10. `app/guardrails/output_validation.py`

```
Validates the output schema and citation IDs.
```

11. `app/services/review_service.py`

```
Saves the result and marks it `pending_approval`.
```

12. `app/api/routes/reviews.py` → `review_service.decide()`

```
An authorized human approves or rejects; the decision and audit event are saved.
```

# 21. What this project already demonstrates — and what it doesn't yet

It is important to distinguish a working reference implementation from a hardened enterprise platform.

|
Capability

|

Current state

|
| --- | --- |
|

FastAPI API and request schemas

|

Included

|
|

Multiple specialized agent modules

|

Included

|
|

LangGraph orchestration

|

Included; linear graph

|
|

Policy retrieval tools

|

Included

|
|

PostgreSQL + pgvector

|

Included

|
|

Redis retrieval cache

|

Included

|
|

Celery background execution

|

Included

|
|

Human approval/rejection endpoints

|

Included

|
|

Output schema and citation checks

|

Included

|
|

Audit-event persistence

|

Included

|
|

Production identity provider

|

Not included

|
|

Durable LangGraph interrupt/resume

|

Not included

|
|

Conditional agent routing / retry loops

|

Not included

|
|

Full policy versioning and approval lifecycle

|

Not included

|
|

Complete observability dashboards and tracing

|

Not included

|
|

Comprehensive evaluation runner

|

Not included

|
|

Production migrations

|

Not included; migration README only

|
|

Calibrated compliance risk model

|

Not included

|

One subtle but important point: the current agent classes are separate logical agents, but they are not all autonomous tool-calling LLM agents. The Policy Research Agent uses application tools; the risk agent is deterministic. This is a reasonable architecture for a controlled compliance workflow, where deterministic steps can be easier to test and audit.

# 22. How I would explain this project in an interview

You can describe it like this:

> “I built a financial compliance review platform using FastAPI, LangGraph, PostgreSQL with pgvector, Redis, and Celery. A user submits financial marketing content, and the system creates a review record. A LangGraph workflow orchestrates specialized stages for claim extraction, policy research, compliance analysis, and risk assessment. The research stage uses tenant-scoped retrieval tools to fetch approved policy evidence from PostgreSQL, using pgvector semantic search when embeddings are available and keyword retrieval as a fallback. The output passes schema and citation-provenance checks before being persisted. The review then enters a pending-approval state, where an authorized human can approve or reject it. Redis provides retrieval caching and the Celery worker supports asynchronous processing. The system records lifecycle actions in an audit table.”

If asked, “Why use multiple agents?”

> “The workflow separates claim identification, evidence gathering, compliance analysis, and risk classification into distinct responsibilities. That makes the system easier to test, inspect, and evolve than one large prompt. LangGraph provides explicit orchestration and shared state, while the tools constrain how the research stage accesses policy data.”

If asked, “Is it production-ready?”

> “It is a runnable reference implementation demonstrating the architecture. Before production, I would replace the demo authentication, add reviewed database migrations, strengthen policy versioning and cache invalidation, add durable workflow checkpoints where required, implement retries and observability, and validate the risk rubric and evaluation dataset with compliance stakeholders.”

## The most important things to understand first

If the architecture feels overwhelming, learn it in this order:

1. FastAPI route → ReviewService: understand how a request becomes a review record.

2. Database models: understand where policies, reviews, and audit events are stored.

3. RAG: understand policy ingestion, embeddings, retrieval, and evidence.

4. Tools: understand how the research agent accesses policy data.

5. Agents: understand the responsibility of each stage.

6. LangGraph state: understand how outputs from one stage become inputs to the next.

7. Guardrails and HITL: understand how the system validates findings and leaves the final decision to a human.

8. Celery and Redis: understand how to run the same workflow asynchronously and cache retrieval results.

The core mental model is simple: FastAPI handles the request, the service manages the review, LangGraph orchestrates the analysis, tools retrieve evidence, PostgreSQL stores the results, and a human makes the final decision.
