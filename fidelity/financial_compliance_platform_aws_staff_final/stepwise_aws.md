# Financial Compliance AI Platform v3.3 – Complete architecture walkthrough

Let's understand this exactly as you would explain it in a Senior/Staff AI Engineer interview.

I have gone through the actual v3.3 project source code, particularly:

- `app/main.py`
- `app/graph/workflow.py`
- `app/graph/runtime.py`
- `app/agents/planner.py`
- `app/agents/supervisor.py`
- `app/agents/specialists.py`
- `app/agents/evaluator.py`
- `app/retrieval/strategies.py`
- `app/retrieval/ingestion.py`
- `app/aws/bedrock_chat.py`
- `app/aws/bedrock_embeddings.py`
- `app/workers/tasks.py`
- `app/workers/outbox.py`

I will explain the actual implementation, not just a theoretical AWS architecture.

The most important thing to understand is:

When a user submits a compliance query, the API does not immediately call an LLM and return an answer. It creates a review, saves the request, queues background execution, retrieves policies, invokes specialist agents, evaluates their findings, validates the evidence and finally waits for a human compliance decision.

That is the central design of your project.

# 1. First understand the complete architecture

Let's take an example.

A compliance officer submits this statement:

> "Our investment product provides guaranteed 15% annual returns with absolutely no investment risk and zero management fees."

The purpose of the application is to determine whether this statement violates financial policies.

Here is the complete flow:

1\. User submits compliance statement

Frontend / Compliance Portal

2\. API Gateway / FastAPI

Authentication · JWT · RBAC · Tenant validation

3\. PostgreSQL

Save review · Audit event · Outbox event

4\. Outbox Publisher + Celery

Publish task through Redis broker

5\. LangGraph Workflow

Retrieve → Plan → Dispatch → Evaluate → Guardrails → HITL

6\. RAG retrieval

Vector Search

pgvector + embeddings

Keyword Search

PostgreSQL

Hybrid retrieval + Reciprocal Rank Fusion

7\. Specialist agents (parallel)

Risk Agent

Fees Agent

Performance Agent

Policy Research Agent

Each agent receives the statement and retrieved policy evidence

8\. Evaluator Agent

Completeness · Evidence validity · Missing agents

9\. Custom Guardrails

Validate findings and policy evidence

10\. Human-in-the-loop approval

LangGraph interrupt and durable checkpoint

11\. PostgreSQL result + Audit

Approved / Rejected / Failed

12\. Frontend receives final result

Now let's understand exactly who calls whom.

# 2. Step 1 – User submits a query

The user enters the following statement:

```
Our investment product provides guaranteed
15% annual returns with absolutely no risk
and zero management fees.
```

The frontend calls:

```
POST /v1/reviews
Authorization: Bearer <JWT_TOKEN>
Idempotency-Key: review-123
Content-Type: application/json
```

Request:

```
{
  "statement": "Our investment product provides guaranteed 15% annual returns with absolutely no risk and zero management fees."
}
```

Who gets called?

Frontend

HTTP POST

FastAPI

app/main.py → create_review()

Authentication and RBAC

require_permission(Permission.REVIEW_CREATE)

Tenant-aware PostgreSQL session

get_tenant_db()

First, the application validates:

1. Is the JWT valid?
2. Who is the user?
3. Which tenant does the user belong to?
4. Does the user have permission to create a review?
5. Has the same idempotency key already been used?

If the request is valid, the application creates three important database records.

| Table           | What gets stored                                             |
| --------------- | ------------------------------------------------------------ |
| `reviews`       | Review ID, tenant ID, user ID, original statement and status |
| `audit_events`  | Who created the review and when                              |
| `outbox_events` | Event saying that this review needs processing               |

The initial status is:

```
QUEUED
```

An example database record:

```
review_id: rev-101
tenant_id: tenant-001
created_by: user-101
status: queued

input_text:
"Our investment product provides guaranteed
15% annual returns..."
```

Important interview point: Where is the user query stored?

It is stored in PostgreSQL in the `reviews.input_text` column.

It is not initially stored in Redis.

Redis is used as the Celery broker/result backend in the existing deployment configuration, not as the authoritative storage for the original review statement.

The API returns:

```
{
  "review_id": "rev-101",
  "status": "queued"
}
```

HTTP status:

```
202 Accepted
```

Why 202?

Because the actual AI processing is asynchronous. The API acknowledges the request without making the user wait for every agent and LLM call to finish.

# 3. Step 2 – Background processing starts

Now the application needs to process the review.

But there is an important design pattern in your project: Transactional Outbox Pattern.

Why do we need it?

Imagine this happens:

- PostgreSQL successfully saves the review.
- The application crashes before sending the Celery task.
- The review exists in the database but is never processed.

This is a reliability problem.

Your project addresses this by saving the review and its outbox event in the same database transaction.

The flow:

PostgreSQL transaction

COMMIT

- Review record
- Audit record
- Outbox record

Celery Beat / Outbox Publisher

app/workers/outbox.py

Read unpublished outbox events

Celery task

reviews.execute

Redis message broker

Celery Worker

app/workers/tasks.py

Let's understand the components:

| Component        | Responsibility                         |
| ---------------- | -------------------------------------- |
| PostgreSQL       | Persist the review and outbox event    |
| Celery Beat      | Trigger periodic outbox publishing     |
| Outbox Publisher | Read unpublished events                |
| Celery           | Dispatch the background task           |
| Redis            | Broker carrying the task message       |
| Celery Worker    | Execute the review-processing function |

The task eventually invokes:

```
invoke_review(    tenant_id="tenant-001",    review_id="rev-101")
```

The implementation is in:

`app/graph/runtime.py`

The worker also claims the review using a database lock and a worker lease to reduce duplicate concurrent processing.

If a worker crashes, Celery retries, and the lease allows another worker to recover the work.

Interview point: I use an asynchronous architecture so that API latency is independent of long-running LLM inference and agent execution.

# 4. Step 3 – LangGraph starts the workflow

Now the Celery worker invokes:

```
workflow.graph.ainvoke(...)
```

This is where Agentic AI orchestration begins.

Your `Workflow` class is in:

```
app/graph/workflow.py
```

It uses LangGraph's `StateGraph`.

Think of LangGraph as the manager responsible for coordinating all the agents.

It maintains a shared state containing information such as:

```
{    "review_id": "rev-101",    "tenant_id": "tenant-001",    "statement": "...",    "policies": [],    "tasks": [],    "outputs": {},    "errors": [],    "step_count": 0,    "rework": 0,    "final_result": None}
```

Each node reads the state and returns updates to it.

The graph has these nodes:

```
START
  |
  v
retrieve
  |
  v
plan
  |
  v
dispatch
  |
  v
evaluate
  |
  +----> rework ----> dispatch
  |
  v
guardrails
  |
  v
human
  |
  v
END
```

There is also a `failed` path when the workflow cannot safely proceed.

Who calls whom?

- `runtime.py` creates the Workflow.
- `Workflow` compiles the LangGraph StateGraph.
- LangGraph executes each node according to the configured edges.
- Each node calls its respective component.

The workflow is not a collection of agents independently calling one another. LangGraph controls the execution order and shared state.

# 5. Step 4 – RAG retrieval: finding the right policies

Very important interview topic

Before agents start their work, they need relevant compliance policies.

For example, the system must find policies related to:

- Guaranteed investment returns.
- Risk disclosures.
- Management fees.
- Investment product suitability.

The workflow calls:

```
policies = await self.loader(    tenant_id,    statement)
```

The loader is defined in:

```
app/graph/runtime.py
```

It calls the retrieval components in:

```
app/retrieval/strategies.py
```

### What happens inside RAG?

Your application implements hybrid retrieval.

It uses two search strategies.

A. Vector search

First, the system converts the user's statement into an embedding.

If AWS is configured:

```
EMBEDDING_PROVIDER=bedrock
```

It calls:

```
BedrockEmbedder.embed_query()
```

This calls:

```
Amazon Bedrock Runtime
    |
    v
Titan Text Embeddings
    |
    v
1536-dimensional vector
```

For example:

```
[0.012, -0.045, 0.087, ...]
```

The vector represents the semantic meaning of the query.

Next, PostgreSQL with pgvector compares the query vector against stored policy embeddings using cosine distance.

It retrieves the most semantically similar policy chunks.

B. Keyword search

At the same time, the system performs lexical search against PostgreSQL.

For example, it looks for terms such as:

- guaranteed
- returns
- risk
- fees
- management

The implementation uses PostgreSQL `ILIKE` matching.

This is useful because financial policies often contain exact terms that matter.

C. Reciprocal Rank Fusion (RRF)

Now we have two result lists.

For example:

Vector search results

| Policy                    | Rank |
| ------------------------- | ---- |
| Investment Risk Policy    | 1    |
| Returns Disclosure Policy | 2    |
| Fees Policy               | 3    |

Keyword search results

| Policy                    | Rank |
| ------------------------- | ---- |
| Returns Disclosure Policy | 1    |
| Fees Policy               | 2    |
| Investment Risk Policy    | 3    |

RRF combines the rankings

\\[ RRF(d)=\sum_r\frac{1}{60+rank_r(d)} \\]

The implementation uses an RRF constant of 60.

The system combines the ranking scores and returns the best six policy records to the workflow.

The implementation is:

```
HybridStrategy(    VectorStrategy(get_embedder()),    KeywordStrategy())
```

Why hybrid retrieval?

Vector search understands semantic similarity, whereas keyword search catches exact financial terminology.

Combining both reduces dependence on either search method alone.

### Where are the policies stored?

In your current implementation:

| Data                        | Storage                                   |
| --------------------------- | ----------------------------------------- |
| Original policy document    | Amazon S3, when AWS storage is configured |
| Extracted policy text       | PostgreSQL                                |
| Policy chunks               | PostgreSQL                                |
| Embeddings                  | PostgreSQL pgvector                       |
| Policy metadata             | PostgreSQL                                |
| Original document reference | S3 URI in PostgreSQL                      |

Every policy retrieval is tenant-filtered and restricted to active policies.

### What if Bedrock fails?

Your retrieval strategy has a fallback.

If vector search throws an exception, it logs the error and falls back to keyword retrieval.

This is important because a temporary embedding or vector search failure should not necessarily make the entire compliance application unavailable.

An important accuracy point about v3.3

The current implementation has hybrid retrieval and RRF, but does not yet have a dedicated Cohere or Bedrock reranking stage. It also does not yet implement a full temporal policy selection algorithm. Those would be future enhancements, not capabilities I would claim are already implemented.

# 6. Step 5 – Planner Agent decides what needs to happen

Once the policies are retrieved, the workflow calls:

```
Planner().plan(...)
```

File:

```
app/agents/planner.py
```

The Planner uses:

```
AdaptivePlanner
```

Its job is to determine which specialist agents are relevant to the user's statement.

For our example:

```
Guaranteed 15% returns
No investment risk
Zero management fees
```

The Planner identifies three major concerns:

1. Performance claims.
2. Risk claims.
3. Fee claims.

It also ensures that Policy Research is included.

It produces a task list similar to:

```
[
  {
    "task_id": "task-1",
    "kind": "performance"
  },
  {
    "task_id": "task-2",
    "kind": "risk"
  },
  {
    "task_id": "task-3",
    "kind": "fees"
  },
  {
    "task_id": "task-4",
    "kind": "policy_research"
  }
]
```

Notice something important.

The Planner does not itself execute the specialist agents.

It only creates the execution plan.

Planner = What needs to be done?

Supervisor = Which tasks should execute now?

This separation makes the architecture easier to maintain and extend.

# 7. Step 6 – Supervisor dispatches specialist agents

Now the workflow invokes:

```
Supervisor().route(...)
```

File:

```
app/agents/supervisor.py
```

The Supervisor checks:

- Which tasks are pending?
- Which tasks have completed?
- How many steps have already been executed?
- Is the maximum execution budget exhausted?

It returns the tasks that can run.

Then the dispatch node executes:

```
results = await asyncio.gather(    *(one(task) for task in todo),    return_exceptions=True)
```

This is particularly important.

Your specialist agents execute in parallel, not one after another.

Supervisor

Dispatches four independent tasks

Performance Agent

Guaranteed 15% return

Risk Agent

No investment risk

Fees Agent

Zero management fees

Policy Research Agent

Applicable policy clauses

Shared workflow state

Each agent's output is collected and stored

Let's understand what each agent does.

### A. Performance Agent

It checks whether the statement makes unsupported performance claims.

For example:

```
Guaranteed 15% annual returns.
```

It checks the retrieved policies and produces findings if supported by the evidence.

### B. Risk Agent

It evaluates statements such as:

```
Absolutely no investment risk.
```

It checks the investment risk disclosure requirements.

### C. Fees Agent

It evaluates:

```
Zero management fees.
```

It looks for relevant fee disclosure requirements.

### D. Policy Research Agent

It provides policy-focused analysis and identifies relevant compliance clauses.

### Which LLM do these agents call?

This is where Amazon Bedrock enters the architecture.

Your `LlmSpecialist.run()` checks:

```
settings.llm_provider
```

If:

```
LLM_PROVIDER=bedrock
```

It calls:

```
create_bedrock_chat_model()
```

The call flow becomes:

Risk / Fees / Performance / Policy Agent

LangChain ChatBedrockConverse

Amazon Bedrock Runtime

Configured foundation model

For example, an enabled Claude model

Structured JSON output

Pydantic validates findings and notes

The agent sends:

- Original user statement.
- Retrieved policy text.
- Its specialist role.
- Its system instructions.

The LLM returns structured findings, not just free-form text.

Example:

```
{
  "findings": [
    {
      "category": "risk",
      "severity": "high",
      "statement": "The claim describes the investment as risk-free",
      "rationale": "The claim requires verification against the applicable risk disclosure policy",
      "evidence": [
        {
          "policy_code": "INVESTMENT-RISK",
          "policy_version": "2026.1",
          "quote": "All investment products carry market risk..."
        }
      ]
    }
  ]
}
```

The exact findings depend on the retrieved policies. This is an illustrative response.

Important: Your v3.3 configuration supports both OpenAI and Bedrock. Bedrock is not automatically used just because AWS infrastructure is configured. You must explicitly set `LLM_PROVIDER=bedrock`.

Also, the four agents currently share the same configured model provider and model ID. They are specialized by their instructions and input, not by having four independently deployed foundation models.

# 8. Step 7 – Evaluator checks the agent results

Now all the agents have completed execution.

Their results are collected into the shared LangGraph state.

The workflow invokes:

```
evaluate(    outputs,    findings,    policies,    expected_agents=...)
```

File:

```
app/agents/evaluator.py
```

Think of the Evaluator as the quality-control component.

It checks:

1. Did every expected specialist return an output?
2. Does every finding contain evidence?
3. Does the evidence refer to a retrieved policy?
4. Was policy context available?
5. Are there invalid policy references?

For example:

| Check                       | Result |
| --------------------------- | ------ |
| Performance Agent completed | Pass   |
| Risk Agent completed        | Pass   |
| Fees Agent completed        | Pass   |
| Policy Research completed   | Pass   |
| Evidence available          | Pass   |
| Evidence policy IDs valid   | Pass   |

If evaluation passes, the workflow proceeds to guardrails.

If it fails, the workflow may enter the rework node.

### What is the rework loop?

Suppose the Risk Agent fails.

The Evaluator detects that the required agent output is missing.

The workflow follows:

```
Evaluate
   |
   v
Failed evaluation
   |
   v
Prepare Rework
   |
   v
Dispatch agents again
   |
   v
Evaluate again
```

Your project limits the number of rework attempts using:

```
max_evaluation_reworks
```

The default is one.

This is important because without a maximum limit, agents could enter infinite loops and consume unnecessary tokens and money.

Staff-level interview point: I use bounded retries and evaluator-driven rework rather than allowing an unconstrained autonomous agent loop.

One qualification: the current evaluator is primarily a structural and evidence-reference validator. It does not yet prove that the LLM's interpretation of every policy is legally or semantically correct.

# 9. Step 8 – Guardrails validate the final findings

After evaluation passes, LangGraph calls:

```
validate(    findings,    policies,    tenant_id)
```

File:

```
app/guardrails.py
```

This component provides an additional validation layer.

It checks the findings against the retrieved policy context and tenant boundaries.

The purpose is to prevent unsupported findings from moving into the approval stage.

Think of the difference this way:

| Component      | Responsibility                                                                   |
| -------------- | -------------------------------------------------------------------------------- |
| Evaluator      | Did the agents execute correctly and provide valid evidence references?          |
| Guardrails     | Are the findings acceptable under application-level evidence and security rules? |
| Human reviewer | Should the compliance assessment be approved or rejected?                        |

If guardrails pass, the workflow constructs the final assessment.

Example:

```
{
  "findings": [
    {
      "category": "performance",
      "severity": "high",
      "statement": "Guaranteed 15% annual return"
    },
    {
      "category": "risk",
      "severity": "high",
      "statement": "No investment risk"
    },
    {
      "category": "fees",
      "severity": "medium",
      "statement": "Zero management fees"
    }
  ],
  "policy_versions": [
    "2026.1"
  ]
}
```

This is an illustrative structure, not a claim that these exact findings are always generated.

# 10. Step 9 – Human-in-the-loop approval

This is one of the most important parts of your project.

Financial compliance decisions should not be fully automated by an LLM.

Your workflow uses LangGraph's:

```
interrupt()
```

The Human node pauses the graph and sends a review payload containing:

- Review ID.
- Assessment.
- Findings.
- Reviewer decision requirement.

The state is saved through:

```
AsyncPostgresSaver
```

This is a PostgreSQL-backed LangGraph checkpointer.

Agent analysis completed

LangGraph interrupt()

Workflow pauses and checkpoint is persisted

Compliance officer reviews assessment

Approve

Reject

Resume LangGraph checkpoint

### What happens when the reviewer approves?

The frontend sends:

```
POST /v1/reviews/rev-101/decision
```

Request:

```
{
  "decision": "approve",
  "comment": "Compliance assessment reviewed and approved."
}
```

FastAPI checks:

- Does the review exist?
- Does the user have approval permission?
- Is the review awaiting a decision?
- Is the reviewer different from the person who created it?

This last check is important for separation of duties.

The API then creates another outbox event:

```
reviews.resume
```

The Outbox Publisher sends the task to Celery.

The Celery worker calls:

```
invoke_review(    tenant_id,    review_id,    decision)
```

Now comes the important part.

The runtime retrieves the saved LangGraph checkpoint using:

```
workflow.graph.aget_state(config)
```

Then it resumes execution using:

```
workflow.graph.ainvoke(    Command(resume=decision),    config=config)
```

This resumes the existing workflow from the interrupt rather than executing all the agents again.

The final status becomes:

```
approved
```

or:

```
rejected
```

Interview point: I use durable workflow checkpoints so that long-running AI workflows can pause for human approval and resume without repeating expensive LLM calls.

# 11. Step 10 – Store the final result and return it to the user

Once the graph completes, the runtime updates PostgreSQL.

The review record stores:

```
review_id: rev-101
status: approved
result_json: final assessment JSON
```

An audit event is also created.

The frontend can retrieve the status using:

```
GET /v1/reviews/rev-101
```

The API calls:

```
SqlReviewRepository(db).get(...)
```

It reads the review from PostgreSQL and returns the result.

Example response:

```
{
  "review_id": "rev-101",
  "status": "approved",
  "result": {
    "findings": [
      {
        "category": "performance",
        "severity": "high",
        "statement": "Guaranteed 15% annual returns"
      },
      {
        "category": "risk",
        "severity": "high",
        "statement": "No investment risk"
      }
    ],
    "human_decision": {
      "decision": "approve",
      "comment": "Compliance assessment reviewed and approved."
    }
  }
}
```

The final result is available to the compliance officer.

Remember the three different statuses:

| Status        | Meaning                                               |
| ------------- | ----------------------------------------------------- |
| `needs_human` | AI analysis completed and is waiting for human review |
| `approved`    | Human reviewer approved the assessment                |
| `rejected`    | Human reviewer rejected the assessment                |
| `failed`      | Workflow could not complete successfully              |

The user can also retrieve the audit history through:

```
GET /v1/reviews/{review_id}/audit
```

# 12. Where exactly do AWS services enter this architecture?

This is a question an interviewer may ask:

"You have mentioned AWS Bedrock, S3, Textract, ECS, Redis and PostgreSQL. How are they actually integrated?"

Let's separate the services into two categories.

## A. AWS services already integrated in v3.3

| AWS service            | Exact integration               | When it is called                             |
| ---------------------- | ------------------------------- | --------------------------------------------- |
| Amazon S3              | `app/aws/storage.py`            | Original policy document upload               |
| Amazon Textract        | `app/aws/textract.py`           | Scanned PDF extraction                        |
| Amazon Bedrock Runtime | `app/aws/bedrock_chat.py`       | Agent LLM inference when configured           |
| Amazon Bedrock Runtime | `app/aws/bedrock_embeddings.py` | Query and document embeddings when configured |
| AWS KMS                | S3 storage configuration        | Encryption, when configured                   |
| AWS IAM                | Terraform task-role resources   | AWS service permissions                       |

### Important: Document upload is a separate workflow

You should understand this distinction.

The user query flow does not normally call Textract.

Textract is called when a document is uploaded and cannot be extracted through the local parser.

For example:

```
Compliance Officer uploads PDF
           |
           v
FastAPI /documents/upload
           |
           v
Amazon S3
           |
           v
Local document parser
           |
           +---- Text extracted?
           |          |
           |         Yes
           |          |
           |          v
           |       Continue
           |
           +---- No (scanned PDF)
                      |
                      v
                Amazon Textract
                      |
                      v
                Extracted text
                      |
                      v
                Chunking
                      |
                      v
                Bedrock embeddings
                      |
                      v
                PostgreSQL + pgvector
```

The original document stays in S3. Extracted text and embeddings are stored in PostgreSQL.

Later, when the user submits a compliance query, the retrieval component accesses PostgreSQL rather than sending the original PDF to Textract again.

## B. AWS services that are deployment targets or future integrations

This distinction is very important in interviews.

Your v3.3 code does not automatically integrate every AWS service we discussed earlier.

| AWS service               | Current status in v3.3                                            |
| ------------------------- | ----------------------------------------------------------------- |
| ECS Fargate               | Deployment target                                                 |
| RDS / Aurora PostgreSQL   | Deployment target; current application uses configured PostgreSQL |
| ElastiCache               | Deployment target; Redis-compatible backend                       |
| SQS                       | Not wired into current outbox dispatcher                          |
| EventBridge               | Not wired into current review execution flow                      |
| Step Functions            | Not used for LangGraph orchestration                              |
| OpenSearch Serverless     | Optional future retrieval alternative                             |
| Bedrock Knowledge Bases   | Optional future RAG alternative                                   |
| Bedrock AgentCore Runtime | Not enabled                                                       |
| Bedrock AgentCore Gateway | Not enabled                                                       |
| CloudWatch / X-Ray        | Deployment and observability enhancements, not fully wired        |

How to explain this professionally:

"We designed the system with a modular AWS adapter layer. Bedrock, S3 and Textract are implemented integrations. The container, database, queue and observability services have deployment configurations or documented migration paths. We deliberately kept LangGraph as the single workflow orchestrator and PostgreSQL as the system of record instead of duplicating responsibilities across AWS services."

That is a much stronger answer than claiming all AWS services are already deployed.

# 13. Complete call chain – remember this for interviews

This is the most useful table to revise before your interview.

| Step | Component called        | Who calls it?      | Responsibility                              |
| ---- | ----------------------- | ------------------ | ------------------------------------------- |
| 1    | `create_review()`       | Frontend → FastAPI | Accept user query                           |
| 2    | JWT + RBAC              | FastAPI dependency | Authenticate and authorize                  |
| 3    | PostgreSQL              | FastAPI            | Save review and outbox event                |
| 4    | Outbox Publisher        | Celery Beat        | Publish pending events                      |
| 5    | Celery task             | Outbox Publisher   | Queue review execution                      |
| 6    | Redis                   | Celery             | Transport task messages                     |
| 7    | `invoke_review()`       | Celery worker      | Start workflow execution                    |
| 8    | `Workflow.graph`        | Runtime            | Execute LangGraph                           |
| 9    | `retrieve()`            | LangGraph          | Retrieve relevant policies                  |
| 10   | `HybridStrategy`        | Retrieval loader   | Vector + keyword retrieval                  |
| 11   | Bedrock Embeddings      | Vector strategy    | Convert query into vector, if configured    |
| 12   | `Planner`               | LangGraph          | Create specialist tasks                     |
| 13   | `Supervisor`            | LangGraph          | Select runnable tasks                       |
| 14   | Specialist agents       | Dispatch node      | Perform compliance analysis                 |
| 15   | Bedrock Chat            | Specialist agents  | Generate structured findings, if configured |
| 16   | `Evaluator`             | LangGraph          | Validate execution and evidence references  |
| 17   | Rework node             | LangGraph          | Retry bounded failed analysis               |
| 18   | `Guardrails`            | LangGraph          | Validate evidence and security constraints  |
| 19   | `interrupt()`           | Human node         | Pause for compliance approval               |
| 20   | PostgreSQL checkpointer | LangGraph          | Persist workflow state                      |
| 21   | Decision API            | Human reviewer     | Submit approval/rejection                   |
| 22   | Outbox + Celery         | FastAPI            | Queue workflow resumption                   |
| 23   | `Command(resume=...)`   | Runtime            | Resume saved graph                          |
| 24   | PostgreSQL              | Runtime            | Save final result and audit                 |
| 25   | GET review API          | Frontend           | Retrieve final assessment                   |

# 14. How to explain this in an interview – 3-minute answer

Here is the answer I would recommend practising. It is written in a natural speaking style rather than documentation language.

Interview answer

Practice this

I have designed an enterprise financial compliance platform using FastAPI, LangGraph, PostgreSQL, Redis and Amazon Bedrock.

The main objective is to analyse financial statements and marketing materials against internal compliance policies and identify potential violations with supporting evidence.

Let me explain the end-to-end architecture.

First, when a compliance officer submits a statement, the request reaches our FastAPI application. We validate the JWT, user permissions and tenant context using RBAC.

We then persist the original statement, review metadata, audit event and an outbox event in PostgreSQL within the same transaction. We use the transactional outbox pattern to avoid losing background processing events.

A background publisher reads pending outbox events and dispatches Celery tasks through Redis. The Celery worker picks up the task and invokes our LangGraph workflow.

The first stage in LangGraph is RAG retrieval.

We use hybrid retrieval combining semantic vector search and keyword search. For semantic search, we generate embeddings using Amazon Bedrock Titan when the Bedrock provider is enabled. The embeddings are stored in PostgreSQL using pgvector.

In parallel, we perform keyword search using PostgreSQL. We combine both result sets using Reciprocal Rank Fusion and retrieve the most relevant policy chunks. All retrieval is tenant-scoped.

Once we have the policy context, the Planner determines which specialist agents are required. Our Supervisor then dispatches those agents.

We currently have Performance, Risk, Fees and Policy Research agents. They execute concurrently using asynchronous execution. Each specialist receives the original statement and the retrieved policy evidence.

For LLM inference, we use Amazon Bedrock through LangChain's ChatBedrockConverse integration when configured. The agents return structured findings with severity, rationale and supporting policy references.

After execution, our Evaluator checks agent completeness and evidence validity. If required outputs are missing or evidence references are invalid, we allow a bounded rework cycle.

Once evaluation passes, our application-level guardrails validate the findings and evidence.

Because this is a financial compliance system, we don't allow the LLM to make the final approval decision autonomously.

We use LangGraph's interrupt mechanism to pause execution and persist the workflow checkpoint in PostgreSQL.

A compliance officer then reviews the findings and either approves or rejects them. The decision is submitted through our API, queued through the outbox and Celery, and the workflow resumes from the saved checkpoint.

Finally, we persist the decision, final assessment and audit events in PostgreSQL. The frontend retrieves the result through our review-status API.

From a reliability perspective, we have idempotency keys, transactional outbox, worker leases, retry mechanisms, durable LangGraph checkpoints and bounded agent execution.

From a security perspective, we enforce tenant isolation, RBAC, evidence validation and controlled AWS service permissions.

The architecture separates API handling, agent orchestration, retrieval, model inference, background execution and human approval, which allows us to scale and evolve each component independently.

# 15. Interview questions you should be prepared for

These are the questions an interviewer is likely to ask after you explain this architecture.

1\. Why did you choose LangGraph instead of a normal LangChain chain?

2\. Why do you use both vector and keyword search?

3\. Why not call the LLM directly from FastAPI?

4\. How do you prevent duplicate execution?

5\. What happens if a worker crashes?

6\. What happens if Bedrock is unavailable?

7\. How do you prevent hallucinations?

8\. Why use human-in-the-loop?

9\. Why PostgreSQL instead of storing everything in Redis?

10\. How would you scale this to millions of requests?

# 16. Five things you must never confuse

1. LangGraph vs Bedrock: LangGraph controls agent workflow execution; Bedrock provides LLM inference.
2. PostgreSQL vs Redis: PostgreSQL stores durable business and workflow data; Redis transports background tasks.
3. S3 vs pgvector: S3 stores original documents; pgvector stores their embeddings.
4. Planner vs Supervisor: Planner decides what work is required; Supervisor decides which tasks to execute.
5. Evaluator vs Human Reviewer: Evaluator checks technical completeness and evidence references; the human reviewer makes the approval decision.

## My final advice

Don't try to memorize 30 AWS services. Understand these six things extremely well:

- How the request enters and gets stored.
- How the transactional outbox and Celery worker work.
- How hybrid RAG retrieves the correct policies.
- How LangGraph coordinates the specialist agents.
- How evaluation, guardrails and HITL work.
- How the workflow recovers from failures.

If you can draw the architecture on a whiteboard and explain who calls whom, why each component exists, and what happens when something fails, you will have a much stronger Staff-level interview discussion.

One particularly useful next exercise: practise explaining this same architecture with a failure scenario, such as Bedrock becoming unavailable while three specialist agents are executing. That is where interviewers can distinguish someone who knows the technology names from someone who understands production AI systems.