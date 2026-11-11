Let's understand this from the actual user's query execution perspective. Imagine you are sitting in a Staff AI Engineer interview at Fidelity, and the interviewer asks:

"Suppose a financial advisor submits a query to your platform. Explain exactly what happens internally. Which component gets called first? Who calls whom? How does the request reach the agents, and how does the response come back?"

I'll explain it step by step, including the actual function responsibilities, data passed between components, and failure scenarios.

# 1. First, understand the complete execution flow

Suppose the advisor submits this query:

Example user query

"Can I recommend ABC Growth Fund to a conservative investor with a $1 million portfolio? The fund has generated 18% annual returns and has very low risk."

The high-level execution flow is:

1

React / Angular frontend

User submits query

2

FastAPI API endpoint

Receives and validates request

3

Authentication and RBAC

Validates identity, role and tenant

4

PostgreSQL

Persists original query and review

5

Transactional Outbox

Creates reliable background event

6

Redis + Celery

Dispatches review task

7

Celery Worker

Starts AI workflow

8

LangGraph Runtime

Creates and executes graph state

9

Policy Retrieval / RAG

Retrieves relevant policy documents

10

Adaptive Planner

Selects required specialist tasks

11

Supervisor

Dispatches specialist agents

12

Specialist Agents

Analyze risk, performance, fees and policies

13

Evaluator

Checks agent outputs and evidence

14

Guardrails

Validates evidence and policy references

15

Human Approval

Pauses for compliance decision

16

PostgreSQL

Persists final decision and audit

17

FastAPI

Returns review result to frontend

Now let's understand every step.

# 2. Detailed execution: Who calls whom?

## Step 1. User submits a query from the frontend

The advisor opens the application and enters:

```
Can I recommend ABC Growth Fund to a conservative
investor with a $1 million portfolio?

The fund has generated 18% annual returns
and has very low risk.
```

The frontend makes an HTTP request.

```
POST /v1/reviews
Authorization: Bearer <JWT_TOKEN>
Idempotency-Key: abc-123
Content-Type: application/json
```

Request body:

```
{
  "statement": "Can I recommend ABC Growth Fund to a conservative investor with a $1 million portfolio? The fund has generated 18% annual returns and has very low risk."
}
```

Who calls whom?

`Frontend → FastAPI`

The frontend does not call LangGraph or the LLM directly.

It only communicates with our backend APIs.

## Step 2. FastAPI receives the request

The request enters the FastAPI application.

The API endpoint is:

```
POST /v1/reviews
```

The API performs:

1. Request schema validation using Pydantic.
2. JWT authentication.
3. Role authorization.
4. Tenant identification.
5. Idempotency validation.

For example, the backend extracts:

```
tenant_id = "institution-001"user_id = "advisor-101"role = "analyst"statement = request.statement
```

If authentication fails, the API returns 401.

If the user doesn't have permission, it returns 403.

If the request is malformed, it returns 422.

Who calls whom?

`FastAPI Endpoint → Authentication → RBAC → Review Service`

The review service is responsible for business-level request processing.

## Step 3. Review Service saves the query in PostgreSQL

This is an important part of your architecture.

The Review Service creates a review record.

For example:

```
review = Review(    tenant_id=tenant_id,    created_by=user_id,    input_text=statement,    status="queued")
```

It also creates:

- An audit event.
- An idempotency record.
- An outbox event.

All these records are saved within one PostgreSQL transaction.

Example database record:

| Column      | Value               |
| ----------- | ------------------- |
| review_id   | REV-1001            |
| tenant_id   | institution-001     |
| created_by  | advisor-101         |
| input_text  | Original user query |
| status      | queued              |
| result_json | NULL                |

Why PostgreSQL?

Because the original user query, review status and final compliance decision are business records. They must be persisted reliably.

Who calls whom?

`Review Service → SQLAlchemy Repository → PostgreSQL`

At this point, we haven't called any LLM.

## Step 4. Transactional Outbox publishes the event

Now we need to execute the AI workflow.

But we don't want to run it inside the HTTP request.

Why?

Because multiple LLM calls, retrieval and agent execution may take several seconds.

Instead, the transaction has already created an outbox event:

```
{
  "event_type": "review.created",
  "review_id": "REV-1001",
  "tenant_id": "institution-001"
}
```

The Outbox Publisher periodically reads unpublished events.

It publishes the task to the Celery queue using Redis as the broker.

Who calls whom?

`Outbox Publisher → Redis Broker`

If Redis is down, the event remains pending in PostgreSQL and can be retried.

This prevents us from losing a review between database persistence and task publication.

## Step 5. Celery Worker receives the task

A Celery worker listens to the review queue.

It receives something like:

```
{
  "review_id": "REV-1001",
  "tenant_id": "institution-001"
}
```

The worker executes the review task.

Conceptually:

```
execute_review.delay(    review_id="REV-1001",    tenant_id="institution-001")
```

The worker then calls the graph runtime.

Who calls whom?

`Redis → Celery Worker → Graph Runtime`

The worker is not responsible for deciding whether the investment is compliant.

Its responsibility is to execute the workflow reliably.

# 3. Now the actual AI workflow starts

This is the most important section for your interview.

## Step 6. Graph Runtime initializes LangGraph

The Celery worker calls the runtime:

```
invoke_review(    tenant_id="institution-001",    review_id="REV-1001")
```

The runtime loads the review from PostgreSQL.

It initializes the graph state.

For example:

```
state = {    "review_id": "REV-1001",    "tenant_id": "institution-001",    "statement": "Can I recommend ABC Growth Fund...",    "policies": [],    "tasks": [],    "outputs": {},    "errors": [],    "findings": [],    "step_count": 0,    "rework": 0}
```

It also configures the durable graph thread.

```
config = {    "configurable": {        "thread_id": "institution-001:review:REV-1001"    }}
```

Why thread ID?

Because LangGraph needs a stable identifier to associate workflow checkpoints with a particular review.

If the worker crashes, we can recover the same workflow thread.

Who calls whom?

`Celery Worker → Graph Runtime → LangGraph`

## Step 7. LangGraph calls the retrieval node

The first major graph node is the policy retrieval node.

It takes the user's statement and searches for applicable policies.

For example, it identifies these important concepts:

- Conservative investor.
- High-risk investment.
- 18% historical returns.
- Investment suitability.
- Risk disclosure.

The retrieval service creates an embedding of the query and searches PostgreSQL/pgvector.

It also performs keyword retrieval.

The results are merged using Reciprocal Rank Fusion.

Example retrieved policies:

Retrieved policy 1

`INV-SUIT-001`

Conservative clients may allocate up to 10% of their portfolio to high-risk investments.

Relevant evidence

Retrieved policy 2

`INV-RISK-002`

Financial communications must accurately disclose investment risk classifications.

Relevant evidence

Retrieved policy 3

`INV-PERF-003`

Historical performance claims must be supported by approved performance records.

The retrieval service returns the relevant policy chunks to LangGraph.

LangGraph stores them in:

```
state["policies"]
```

Who calls whom?

`LangGraph Retrieval Node → Retrieval Service → Embedding Model → PostgreSQL/pgvector`

The retrieval service also performs keyword search and combines the results.

Important: the LLM has not yet analyzed the investment.

We are first establishing the authoritative context.

## Step 8. LangGraph calls the Adaptive Planner

Now the Planner receives:

- Original advisor query.
- Retrieved policies.
- Available portfolio context.
- Available specialist capabilities.

It determines what needs to be analyzed.

For our example, it identifies:

| Task                 | Why required                           |
| -------------------- | -------------------------------------- |
| Risk analysis        | User claims the fund has very low risk |
| Performance analysis | User claims 18% returns                |
| Policy research      | Conservative investor suitability      |
| Portfolio analysis   | Portfolio allocation assessment        |
| Claim verification   | Verify material financial statements   |

The standalone adaptive planner supports these capabilities.

However, our current graph integration only dispatches four specialist types: Risk, Performance, Fees and Policy Research.

Portfolio analytics and claim verification still need to be wired into the graph.

This is a distinction you should be aware of in your interview.

Who calls whom?

`LangGraph → Adaptive Planner → Task Plan → LangGraph State`

The planner does not directly execute the agents.

It produces the execution plan.

## Step 9. LangGraph calls the Supervisor

Now the Supervisor receives the planned tasks.

Its responsibility is to coordinate execution.

It checks:

- Which tasks are supported?
- Which tasks have already completed?
- Which tasks remain pending?
- Is the maximum execution budget reached?
- Can tasks run in parallel?

For example:

```
tasks = [    "risk",    "performance",    "policy_research"]
```

The Supervisor dispatches these tasks to the specialist agents.

Who calls whom?

`LangGraph → Supervisor → Specialist Agents`

The Supervisor is a deterministic orchestration component, not necessarily an LLM.

## Step 10. Specialist agents execute in parallel

Now the interesting part begins.

We have four specialist agents.

Risk Agent

High-risk finding

It receives the advisor's statement and applicable risk policies.

It analyzes whether describing a high-risk fund as very low risk is supported.

Performance Agent

It examines whether the 18% annual-return statement is supported by approved performance evidence, including the reporting period and date.

Fees Agent

It examines fees and exit-charge claims when relevant.

Policy Research Agent

It checks the applicable suitability and disclosure policies.

### How do they execute simultaneously?

We use asynchronous Python.

Conceptually:

```
results = await asyncio.gather(    risk_agent.run(input_data),    performance_agent.run(input_data),    fees_agent.run(input_data),    policy_agent.run(input_data),    return_exceptions=True)
```

The actual project uses a supervisor dispatch abstraction with the same parallel-execution principle.

Each agent returns structured results.

For example:

```
{
  "agent": "risk",
  "findings": [
    {
      "severity": "high",
      "category": "risk_disclosure",
      "description": "The low-risk claim requires verification."
    }
  ]
}
```

The outputs are combined and written into:

```
state["outputs"]
```

Who calls whom?

`Supervisor → Risk Agent`

`Supervisor → Performance Agent`

`Supervisor → Fees Agent`

`Supervisor → Policy Research Agent`

The agents do not need to call each other.

They work independently and return their outputs to the graph.

# 4. Evaluation and validation

## Step 11. LangGraph calls the Evaluator

After the agents finish, LangGraph moves to the evaluation node.

The Evaluator checks whether the agent results are complete and sufficiently supported.

For example:

| Check                                | Result          |
| ------------------------------------ | --------------- |
| Risk Agent returned output           | Pass            |
| Performance Agent returned output    | Pass            |
| Policy Agent returned output         | Pass            |
| Required evidence present            | Must be checked |
| Evidence references retrieved policy | Must be checked |

Suppose the Risk Agent returns:

"35% allocation is not suitable."

But it doesn't provide any evidence.

The evaluator rejects the current output.

It returns something conceptually like:

```
{
  "passed": false,
  "reason": "Missing evidence reference",
  "rework_required": true
}
```

Who calls whom?

`LangGraph → Evaluator → LangGraph`

## Step 12. Conditional routing — Rework or continue?

This is where LangGraph becomes particularly useful.

It doesn't always follow the same path.

If evaluation fails, the graph routes to the rework node.

If evaluation passes, it proceeds to guardrails.

\#chatgpt-mermaid-\_r_13j\_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(237, 237, 237);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-\_r_13j\_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_13j\_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_13j\_ .error-icon{fill:rgb(48, 48, 48);}#chatgpt-mermaid-\_r_13j\_ .error-text{fill:rgb(237, 237, 237);stroke:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_13j\_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-\_r_13j\_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-\_r_13j\_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-\_r_13j\_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-\_r_13j\_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-\_r_13j\_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-\_r_13j\_ .marker{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_13j\_ .marker.cross{stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_13j\_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-\_r_13j\_ p{margin:0;}#chatgpt-mermaid-\_r_13j\_ .label{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_13j\_ .cluster-label text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_13j\_ .cluster-label span{color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_13j\_ .cluster-label span p{background-color:transparent;}#chatgpt-mermaid-\_r_13j\_ .label text,#chatgpt-mermaid-\_r_13j\_ span{fill:rgb(237, 237, 237);color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_13j\_ .node rect,#chatgpt-mermaid-\_r_13j\_ .node circle,#chatgpt-mermaid-\_r_13j\_ .node ellipse,#chatgpt-mermaid-\_r_13j\_ .node polygon,#chatgpt-mermaid-\_r_13j\_ .node path{fill:rgb(9, 23, 44);stroke:rgb(31, 78, 148);stroke-width:1px;}#chatgpt-mermaid-\_r_13j\_ .rough-node .label text,#chatgpt-mermaid-\_r_13j\_ .node .label text,#chatgpt-mermaid-\_r_13j\_ .image-shape .label,#chatgpt-mermaid-\_r_13j\_ .icon-shape .label{text-anchor:middle;}#chatgpt-mermaid-\_r_13j\_ .node .katex path{fill:#000;stroke:#000;stroke-width:1px;}#chatgpt-mermaid-\_r_13j\_ .rough-node .label,#chatgpt-mermaid-\_r_13j\_ .node .label,#chatgpt-mermaid-\_r_13j\_ .image-shape .label,#chatgpt-mermaid-\_r_13j\_ .icon-shape .label{text-align:center;}#chatgpt-mermaid-\_r_13j\_ .node.clickable{cursor:pointer;}#chatgpt-mermaid-\_r_13j\_ .root .anchor path{fill:rgb(175, 175, 175)!important;stroke-width:0;stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_13j\_ .arrowheadPath{fill:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_13j\_ .edgePath .path{stroke:rgb(175, 175, 175);stroke-width:1px;}#chatgpt-mermaid-\_r_13j\_ .flowchart-link{stroke:rgb(175, 175, 175);fill:none;}#chatgpt-mermaid-\_r_13j\_ .edgeLabel{background-color:rgb(0, 0, 0);text-align:center;}#chatgpt-mermaid-\_r_13j\_ .edgeLabel p{background-color:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_13j\_ .edgeLabel rect{opacity:0.5;background-color:rgb(0, 0, 0);fill:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_13j\_ .labelBkg{background-color:rgba(0, 0, 0, 0.5);}#chatgpt-mermaid-\_r_13j\_ .cluster rect{fill:rgb(48, 48, 48);stroke:rgba(255, 255, 255, 0.15);stroke-width:1px;}#chatgpt-mermaid-\_r_13j\_ .cluster text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_13j\_ .cluster span{color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_13j\_ div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:12px;background:rgb(48, 48, 48);border:1px solid rgba(255, 255, 255, 0.15);border-radius:2px;pointer-events:none;z-index:100;}#chatgpt-mermaid-\_r_13j\_ .flowchartTitleText{text-anchor:middle;font-size:18px;fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_13j\_ rect.text{fill:none;stroke-width:0;}#chatgpt-mermaid-\_r_13j\_ .icon-shape,#chatgpt-mermaid-\_r_13j\_ .image-shape{background-color:rgb(0, 0, 0);text-align:center;}#chatgpt-mermaid-\_r_13j\_ .icon-shape p,#chatgpt-mermaid-\_r_13j\_ .image-shape p{background-color:rgb(0, 0, 0);padding:2px;}#chatgpt-mermaid-\_r_13j\_ .icon-shape .label rect,#chatgpt-mermaid-\_r_13j\_ .image-shape .label rect{opacity:0.5;background-color:rgb(0, 0, 0);fill:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_13j\_ .label-icon{display:inline-block;height:1em;overflow:visible;vertical-align:-0.125em;}#chatgpt-mermaid-\_r_13j\_ .node .label-icon path{fill:currentColor;stroke:revert;stroke-width:revert;}#chatgpt-mermaid-\_r_13j\_ .node .neo-node{stroke:rgb(31, 78, 148);}#chatgpt-mermaid-\_r_13j\_ [data-look="neo"].node rect,#chatgpt-mermaid-\_r_13j\_ [data-look="neo"].cluster rect,#chatgpt-mermaid-\_r_13j\_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-\_r_13j\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_13j\_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-\_r_13j\_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-\_r_13j\_-gradient);stroke-width:1px;}#chatgpt-mermaid-\_r_13j\_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_13j\_ [data-look="neo"].node .neo-line path{stroke:rgb(31, 78, 148);filter:none;}#chatgpt-mermaid-\_r_13j\_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-\_r_13j\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_13j\_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-\_r_13j\_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-\_r_13j\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_13j\_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-\_r_13j\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_13j\_ .node text{font-size:14px;font-weight:600;letter-spacing:normal;fill:rgb(153, 206, 255);}#chatgpt-mermaid-\_r_13j\_ .edgeLabels text{font-size:13px;font-weight:600;letter-spacing:-0.08px;fill:rgb(153, 206, 255);}#chatgpt-mermaid-\_r_13j\_ .node tspan[font-weight="normal"],#chatgpt-mermaid-\_r_13j\_ .edgeLabels tspan[font-weight="normal"]{font-weight:600;}#chatgpt-mermaid-\_r_13j\_ .edgeLabel .label rect{opacity:1;rx:13px;ry:13px;fill:rgb(0, 14, 26);stroke:rgb(26, 62, 95);stroke-width:1px;}#chatgpt-mermaid-\_r_13j\_ .node rect,#chatgpt-mermaid-\_r_13j\_ .node circle,#chatgpt-mermaid-\_r_13j\_ .node ellipse,#chatgpt-mermaid-\_r_13j\_ .node polygon,#chatgpt-mermaid-\_r_13j\_ .node path{fill:rgb(0, 40, 77);stroke:rgba(255, 255, 255, 0.1);stroke-width:1px;}#chatgpt-mermaid-\_r_13j\_ .node rect{rx:16px;ry:16px;}#chatgpt-mermaid-\_r_13j\_ .mermaid-decision .label-container{fill:rgb(0, 14, 26);stroke:rgb(26, 62, 95);stroke-dasharray:2,2;}#chatgpt-mermaid-\_r_13j\_ .edgePaths .flowchart-link{stroke:rgb(175, 175, 175);stroke-width:1px;stroke-linecap:round;stroke-linejoin:round;}#chatgpt-mermaid-\_r_13j\_ .marker{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_13j\_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}Specialist outputsEvaluatorPassed?Retry budget available?Prepare reworkSupervisor dispatchMark review failedGuardrailsValid?Human approvalNoYesNoYesNoYes

For example:

- First attempt: Risk Agent doesn't return sufficient evidence.
- Evaluator rejects.
- Rework counter increases.
- Supervisor dispatches the required work again.
- Second attempt: Evidence is supplied.
- Evaluator passes.

We have a bounded retry mechanism.

We don't let the agents run indefinitely.

## Step 13. Guardrails validate the findings

After evaluation passes, the guardrail node checks the evidence.

It validates:

- Policy ID.
- Tenant ownership.
- Policy version.
- Exact source quotation.
- Evidence availability.

Imagine an LLM invents this statement:

"The policy prohibits all investments above 15%."

But the actual policy says 10%.

The guardrail detects that the quoted evidence does not match the retrieved policy.

The review is blocked.

This is an important principle:

We use LLMs for reasoning, but deterministic code for enforcing compliance invariants.

The advanced semantic evaluator and persistent evidence ledger are additional modules in v3.2, but they are not yet integrated into this active graph path.

# 5. Human approval and final response

## Step 14. LangGraph pauses for human approval

After all automated checks pass, the workflow reaches the Human Approval node.

Here we use LangGraph's interrupt mechanism.

The graph does not finish the review immediately.

It pauses and waits for a compliance officer.

The reviewer sees:

- Original advisor query.
- Risk findings.
- Performance findings.
- Applicable policies.
- Supporting evidence.
- Recommended actions.

The reviewer can:

- Approve.
- Reject.
- Request corrections.

Who calls whom?

`LangGraph → Human Approval Interrupt → Compliance Reviewer`

## Step 15. Reviewer submits a decision

Suppose the reviewer rejects the recommendation.

The frontend sends:

```
POST /v1/reviews/REV-1001/decision
```

```
{
  "decision": "reject",
  "comment": "The proposed recommendation does not satisfy the applicable suitability requirements."
}
```

The decision API validates:

- Reviewer authentication.
- Reviewer permission.
- Tenant ownership.
- Review status.
- Separation of duties.

It then persists the decision and creates the workflow-resume event.

The Celery worker resumes the same graph thread using LangGraph's resume mechanism.

Who calls whom?

`Reviewer → FastAPI Decision API → PostgreSQL Outbox → Celery → LangGraph Resume`

## Step 16. LangGraph saves the final result

The graph resumes and processes the reviewer decision.

The final result is saved in PostgreSQL.

For example:

```
{
  "review_id": "REV-1001",
  "status": "rejected",
  "findings": [
    {
      "category": "risk",
      "severity": "high",
      "description": "Risk disclosure requires correction."
    },
    {
      "category": "suitability",
      "severity": "high",
      "description": "The proposed allocation requires further suitability assessment."
    }
  ],
  "decision": {
    "status": "rejected",
    "reviewer": "compliance-101"
  }
}
```

The advisor then retrieves the result through:

```
GET /v1/reviews/REV-1001
```

FastAPI retrieves the record from PostgreSQL and returns it to the frontend.

Who calls whom?

`LangGraph → Review Persistence → PostgreSQL`

Then:

`Frontend → FastAPI → PostgreSQL → Frontend`

# 6. The complete flow to memorize

This is the most useful diagram for your interview.

\#chatgpt-mermaid-\_r_14c\_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(237, 237, 237);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-\_r_14c\_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_14c\_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_14c\_ .error-icon{fill:rgb(48, 48, 48);}#chatgpt-mermaid-\_r_14c\_ .error-text{fill:rgb(237, 237, 237);stroke:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_14c\_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-\_r_14c\_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-\_r_14c\_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-\_r_14c\_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-\_r_14c\_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-\_r_14c\_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-\_r_14c\_ .marker{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_14c\_ .marker.cross{stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_14c\_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-\_r_14c\_ p{margin:0;}#chatgpt-mermaid-\_r_14c\_ .label{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_14c\_ .cluster-label text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_14c\_ .cluster-label span{color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_14c\_ .cluster-label span p{background-color:transparent;}#chatgpt-mermaid-\_r_14c\_ .label text,#chatgpt-mermaid-\_r_14c\_ span{fill:rgb(237, 237, 237);color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_14c\_ .node rect,#chatgpt-mermaid-\_r_14c\_ .node circle,#chatgpt-mermaid-\_r_14c\_ .node ellipse,#chatgpt-mermaid-\_r_14c\_ .node polygon,#chatgpt-mermaid-\_r_14c\_ .node path{fill:rgb(9, 23, 44);stroke:rgb(31, 78, 148);stroke-width:1px;}#chatgpt-mermaid-\_r_14c\_ .rough-node .label text,#chatgpt-mermaid-\_r_14c\_ .node .label text,#chatgpt-mermaid-\_r_14c\_ .image-shape .label,#chatgpt-mermaid-\_r_14c\_ .icon-shape .label{text-anchor:middle;}#chatgpt-mermaid-\_r_14c\_ .node .katex path{fill:#000;stroke:#000;stroke-width:1px;}#chatgpt-mermaid-\_r_14c\_ .rough-node .label,#chatgpt-mermaid-\_r_14c\_ .node .label,#chatgpt-mermaid-\_r_14c\_ .image-shape .label,#chatgpt-mermaid-\_r_14c\_ .icon-shape .label{text-align:center;}#chatgpt-mermaid-\_r_14c\_ .node.clickable{cursor:pointer;}#chatgpt-mermaid-\_r_14c\_ .root .anchor path{fill:rgb(175, 175, 175)!important;stroke-width:0;stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_14c\_ .arrowheadPath{fill:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_14c\_ .edgePath .path{stroke:rgb(175, 175, 175);stroke-width:1px;}#chatgpt-mermaid-\_r_14c\_ .flowchart-link{stroke:rgb(175, 175, 175);fill:none;}#chatgpt-mermaid-\_r_14c\_ .edgeLabel{background-color:rgb(0, 0, 0);text-align:center;}#chatgpt-mermaid-\_r_14c\_ .edgeLabel p{background-color:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_14c\_ .edgeLabel rect{opacity:0.5;background-color:rgb(0, 0, 0);fill:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_14c\_ .labelBkg{background-color:rgba(0, 0, 0, 0.5);}#chatgpt-mermaid-\_r_14c\_ .cluster rect{fill:rgb(48, 48, 48);stroke:rgba(255, 255, 255, 0.15);stroke-width:1px;}#chatgpt-mermaid-\_r_14c\_ .cluster text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_14c\_ .cluster span{color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_14c\_ div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:12px;background:rgb(48, 48, 48);border:1px solid rgba(255, 255, 255, 0.15);border-radius:2px;pointer-events:none;z-index:100;}#chatgpt-mermaid-\_r_14c\_ .flowchartTitleText{text-anchor:middle;font-size:18px;fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_14c\_ rect.text{fill:none;stroke-width:0;}#chatgpt-mermaid-\_r_14c\_ .icon-shape,#chatgpt-mermaid-\_r_14c\_ .image-shape{background-color:rgb(0, 0, 0);text-align:center;}#chatgpt-mermaid-\_r_14c\_ .icon-shape p,#chatgpt-mermaid-\_r_14c\_ .image-shape p{background-color:rgb(0, 0, 0);padding:2px;}#chatgpt-mermaid-\_r_14c\_ .icon-shape .label rect,#chatgpt-mermaid-\_r_14c\_ .image-shape .label rect{opacity:0.5;background-color:rgb(0, 0, 0);fill:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_14c\_ .label-icon{display:inline-block;height:1em;overflow:visible;vertical-align:-0.125em;}#chatgpt-mermaid-\_r_14c\_ .node .label-icon path{fill:currentColor;stroke:revert;stroke-width:revert;}#chatgpt-mermaid-\_r_14c\_ .node .neo-node{stroke:rgb(31, 78, 148);}#chatgpt-mermaid-\_r_14c\_ [data-look="neo"].node rect,#chatgpt-mermaid-\_r_14c\_ [data-look="neo"].cluster rect,#chatgpt-mermaid-\_r_14c\_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-\_r_14c\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_14c\_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-\_r_14c\_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-\_r_14c\_-gradient);stroke-width:1px;}#chatgpt-mermaid-\_r_14c\_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_14c\_ [data-look="neo"].node .neo-line path{stroke:rgb(31, 78, 148);filter:none;}#chatgpt-mermaid-\_r_14c\_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-\_r_14c\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_14c\_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-\_r_14c\_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-\_r_14c\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_14c\_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-\_r_14c\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_14c\_ .node text{font-size:14px;font-weight:600;letter-spacing:normal;fill:rgb(153, 206, 255);}#chatgpt-mermaid-\_r_14c\_ .edgeLabels text{font-size:13px;font-weight:600;letter-spacing:-0.08px;fill:rgb(153, 206, 255);}#chatgpt-mermaid-\_r_14c\_ .node tspan[font-weight="normal"],#chatgpt-mermaid-\_r_14c\_ .edgeLabels tspan[font-weight="normal"]{font-weight:600;}#chatgpt-mermaid-\_r_14c\_ .edgeLabel .label rect{opacity:1;rx:13px;ry:13px;fill:rgb(0, 14, 26);stroke:rgb(26, 62, 95);stroke-width:1px;}#chatgpt-mermaid-\_r_14c\_ .node rect,#chatgpt-mermaid-\_r_14c\_ .node circle,#chatgpt-mermaid-\_r_14c\_ .node ellipse,#chatgpt-mermaid-\_r_14c\_ .node polygon,#chatgpt-mermaid-\_r_14c\_ .node path{fill:rgb(0, 40, 77);stroke:rgba(255, 255, 255, 0.1);stroke-width:1px;}#chatgpt-mermaid-\_r_14c\_ .node rect{rx:16px;ry:16px;}#chatgpt-mermaid-\_r_14c\_ .mermaid-decision .label-container{fill:rgb(0, 14, 26);stroke:rgb(26, 62, 95);stroke-dasharray:2,2;}#chatgpt-mermaid-\_r_14c\_ .edgePaths .flowchart-link{stroke:rgb(175, 175, 175);stroke-width:1px;stroke-linecap:round;stroke-linejoin:round;}#chatgpt-mermaid-\_r_14c\_ .marker{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_14c\_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}User submits queryFastAPI endpointJWT + RBAC + tenantvalidationReview ServicePostgreSQL: Review + Audit +OutboxOutbox PublisherRedis BrokerCelery WorkerLangGraph RuntimePolicy Retrieval NodeHybrid RAG: Keyword + VectorAdaptive PlannerSupervisorSpecialist AgentsEvaluatorEvaluation passed?Bounded ReworkDeterministic GuardrailsValid evidence?Failed / EscalationHuman Approval InterruptReviewer Decision APIOutbox + Celery ResumeResume LangGraphSave Final Result + AuditAdvisor Retrieves ResultNoYesNoYes

# 7. What to say when the interviewer asks, "Who calls whom?"

Memorize this exact explanation:

When a user submits a financial compliance query, the request first enters our FastAPI application.

FastAPI validates the request, authenticates the user through JWT, checks RBAC permissions and establishes the tenant context.

The Review Service persists the original query, review record, audit event and transactional outbox event in PostgreSQL.

An outbox publisher dispatches the review event to Redis, which acts as the Celery broker. A Celery worker consumes the task and invokes our LangGraph runtime.

The LangGraph runtime initializes the review state and starts the workflow using a durable thread ID.

The first major processing stage retrieves applicable policies using our hybrid RAG implementation, which combines PostgreSQL keyword search and pgvector semantic search through Reciprocal Rank Fusion.

The retrieved context is passed to our adaptive planner. The planner determines which specialist capabilities are relevant. The supervisor validates the task plan and dispatches supported specialists.

Our risk, performance, fees and policy research agents execute independently and can run concurrently. They return structured findings to the LangGraph state.

Once execution completes, the evaluator checks completeness and evidence references. If validation fails, LangGraph conditionally routes the execution through a bounded rework cycle. If it passes, deterministic guardrails validate policy identity, tenant ownership, policy version and source quotations.

After successful validation, the workflow pauses at a human approval interrupt. A compliance reviewer approves or rejects the recommendation through a separate API.

The decision is persisted, an event is published through the outbox, and Celery resumes the same LangGraph thread.

Finally, the workflow stores the final compliance result and audit history in PostgreSQL. The advisor retrieves the result through FastAPI.

The key design principle is that LangGraph orchestrates the AI workflow, PostgreSQL maintains business truth, Celery handles asynchronous execution, and deterministic controls enforce security and compliance independently of LLM reasoning.

# 8. Five important interviewer follow-up questions

| Interviewer asks                | Your key answer                                                         |
| ------------------------------- | ----------------------------------------------------------------------- |
| Does the frontend call the LLM? | No, it calls FastAPI.                                                   |
| Who decides which agents run?   | Adaptive Planner proposes tasks; Supervisor dispatches supported tasks. |
| Who calls the agents?           | LangGraph invokes the Supervisor, which dispatches specialists.         |
| Where is the user query stored? | PostgreSQL `reviews.input_text`.                                        |
| Who makes the final decision?   | Authorized human compliance reviewer, not the LLM.                      |

One final point for your preparation: In your current v3.2 project, the core review workflow is implemented, but the document upload, advanced semantic evaluator, persistent evidence ledger and portfolio analytics still need integration into this execution path. Explain those as extended capabilities until that integration is complete.

My recommendation is to practise explaining Steps 1–16 without looking at the answer. If you can confidently explain the caller, callee, input, output and failure handling at every step, you will be able to handle most architecture walkthrough questions at a Senior or Staff AI Engineer interview.