# Financial Compliance Review Platform v2

Staged, extensible reference implementation. Synthetic policies only; not legal advice or a certified compliance product.

## Architecture
FastAPI/API auth → ReviewService → repositories → PostgreSQL/pgvector.
ReviewService → bounded LangGraph workflow: retrieval → typed plan → allow-listed supervisor → parallel
performance/risk/fees/policy-research specialists → deterministic aggregation → completeness evaluator →
evidence/tenant/version guardrails → human decision. Redis/Celery provide background execution.
Structured logs and OpenTelemetry spans instrument the workflow.

## Phases
1. Foundation: repository interfaces, explicit keyword/vector retrieval strategies, Pydantic contracts,
   validated review status transitions.
2. Planner/Supervisor: typed allow-listed tasks, status tracking, maximum step budget.
3. Specialists: concurrent specialist calls, deterministic aggregation.
4. Evaluator/fallback/HITL: completeness gate, bounded rework, transient Celery retries, persisted human decision.
5. Hardening: JWT/JWKS verification boundary, tenant scoping, policy versions, Alembic, observability,
   evaluation harness, security tests and operations checklist.

## Run
`cp .env.example .env && docker compose up --build`
API docs: http://localhost:8000/docs
`pip install -e ".[dev]" && pytest`
Local dev token: `local-dev-token` (only with `AUTH_MODE=dev`).

## Honest implementation boundary
This is a strong runnable reference/starter, not a fully certified production service. Specialists are
deterministic rules, not LLM-driven autonomous agents. The workflow currently runs inline in the API;
Celery task infrastructure is provided. Durable LangGraph checkpoint resume/interrupt is not wired into
the service lifecycle yet, so HITL is persisted API-level approval, not resumable graph interruption.
Vector strategy is implemented but keyword retrieval is the default until an embedder/ingestion pipeline
is configured. See docs/OPERATIONS.md before production use.



Based on the directory structure provided, this project is designed as an enterprise-grade, asynchronous, multi-agent AI system built specifically for financial regulatory auditing.
Here is a step-by-step breakdown of how the entire architecture and the data flows operate from start to finish.
------------------------------
## 🏛️ The Structural Architecture Overview
The system runs on a Clean/Layered Architecture mixed with an Agentic Workflow pattern.

* The Web Layer (app/api/): Lightweight endpoints that accept file submissions and immediately delegate work.
* The Asynchronous Layer (app/workers/): Driven by Celery, it ensures long-running AI operations do not time out or freeze the API.
* The Orchestration Layer (app/graph/ & app/agents/): Uses a state graph framework (like LangGraph or a custom StateGraph) to chain multiple AI agents together in a controlled, loops-safe process.
* The Core Domain (app/domain/): Holds the explicit rules governing how the system transfers from one state to another (transitions.py).
* The Data Access Layer (app/repositories/): Abstracts database interactions using the Repository pattern via SQLAlchemy.

------------------------------
## 📋 Sample Scenarios & Inputs
To visualize how the project works, let's establish a typical sample input payload sent to the platform:
## 1. Input Context
A compliance officer uploads a 15-page PDF document containing marketing copy, disclosures, and fee structures for a new Exchange-Traded Fund (ETF).
## 2. Input JSON Payload (sent along with the file to POST /api/routes)

{
  "document_id": "doc_98765_etf_marketing",
  "review_type": "Marketing_Material_Audit",
  "regulatory_frameworks": ["SEC_Rule_206_4", "FINRA_Rule_2210"],
  "strictness_level": "High"
}

------------------------------
## 🔄 The End-to-End Execution Flow (Step-by-Step)

[User App / UI] 
       │  (1) Upload Document & Metadata
       ▼
 ┌───────────┐      (2) Trigger Job      ┌──────────────┐
 │  FastAPI  │ ────────────────────────> │ Celery Worker│
 └───────────┘                           └──────┬───────┘
                                                │ (3) Initialize State Graph
                                                ▼
                                         ┌──────────────┐
                                  ┌────> │  Supervisor  │ <────┐
                                  │      └──────┬───────┘      │
                   (4) Assign Task│             │              │(6) Return Output
                                  │             │(4) Assign    │
                                  ▼             ▼              ▼
                           ┌───────────┐ ┌─────────────┐ ┌───────────┐
                           │  Planner  │ │ Specialist1 │ │Specialist2│ ...
                           └───────────┘ └─────────────┘ └───────────┘
                                                │
                                                │(5) Intelligent RAG Lookups
                                                ▼
                                         ┌──────────────┐
                                         │ Vector Store │
                                         └──────────────┘
                                                │
                                                │ (7) Finished Handoff
                                                ▼
                                         ┌──────────────┐
                                         │  Evaluator   │
                                         └──────┬───────┘
                                                │ (8) Verify Safety
                                                ▼
                                         ┌──────────────┐
                                         │  Guardrails  │
                                         └──────┬───────┘
                                                │ (9) Save Result
                                                ▼
                                         ┌──────────────┐
                                         │ Database DB  │
                                         └──────────────┘

## Step 1: Ingestion & Offloading

   1. The client submits the ETF PDF and the JSON metadata to the API (app/api/routes.py).
   2. The route intercepts the payload, triggers a basic authentication check (app/auth.py), and saves the file record via the database layer (app/db/session.py).
   3. Instead of processing the file right there, the API immediately hands off the task to Celery (app/workers/celery_app.py) and returns a tracking status (202 ACCEPTED) back to the client. The user doesn't have to wait.

## Step 2: Activating the Workflow Engine

   1. A background Celery worker picks up the job and activates the Service layer (app/services/review_service.py).
   2. The service creates an execution graph state thread (app/graph/workflow.py).
   3. This graph initializes a tracking object containing the document data, empty arrays for findings, and a dynamic dictionary representing the current active workflow status (app/domain/schemas.py).

## Step 3: Strategic Planning (The Planner Agent)

   1. The graph kicks off by routing to the Planner Agent (app/agents/planner.py).
   2. The Planner reads the user's constraints ("SEC_Rule_206_4", "FINRA_Rule_2210") and inspects the document structure.
   3. It constructs a concrete execution plan:
   * “Sub-task 1: Review sections 2 and 3 for misleading performance charts (FINRA 2210 check).”
      * “Sub-task 2: Analyze section 5 for appropriate boilerplate risk disclosure statements (SEC 206-4 check).”
   
## Step 4: Multi-Agent Handoff & RAG Lookups (The Supervisor & Specialists)

   1. The Supervisor Agent (app/agents/supervisor.py) acts as the traffic controller. It reads the plan generated by the Planner and coordinates the specialized sub-agents.
   2. The Supervisor spins up relevant Specialist Agents (app/agents/specialists.py) sequentially or concurrently:
   * FINRA Specialist takes the performance sections.
      * SEC Specialist takes the disclosure sections.
   3. To do their job effectively without exceeding context windows, the Specialists invoke retrieval algorithms (app/retrieval/strategies.py). This layer pulls past internal precedents, precise regulatory rules text, or compliance guidelines from an external vector store database, merging that context directly into the agent prompts.

## Step 5: Consolidation & Critique (The Evaluator Agent)

   1. The Specialists feed their individual compliance findings back to the workflow state.
   2. The Evaluator Agent (app/agents/evaluator.py) acts as a quality control manager. It looks across all specialist outputs to make sure there are no contradictions, removes duplicate or redundant notices, and ensures the findings match the standard formatting rules of a real financial compliance audit report.

## Step 6: The Boundary Intercept (Guardrails & Observability)

   1. Before the text report leaves the agentic network, it passes through an isolated compliance shield (app/guardrails.py).
   2. The guardrails software executes strict heuristic or structural tests:
   * Hallucination checks: Cross-references citations generated by the agents to make sure they point to actual laws or real lines in the uploaded PDF.
      * PII Redaction: Ensures no confidential investor names or accounts accidentally bled into the output text.
   3. All intermediate agent thoughts, latency metrics, token consumption, and errors are silently captured by the Observability engine (app/observability.py) for administrative telemetry.

## Step 7: State Settlement & Database Persistence

   1. The domain rules layer (app/domain/transitions.py) converts the active graph status from PROCESSING to COMPLETED.
   2. The final structured audit report (complete with severity flags, exact text snippets violated, and proposed compliance corrections) is passed into the repository framework (app/repositories/sqlalchemy.py).
   3. It is securely committed to your database schemas (app/db/models.py).
   4. When the user checks back via the UI using their document ID, the platform displays a completed, accurate compliance report.

------------------------------
## 🎯 Sample Output Generated by this Architecture
Once the pipeline resolves, the final database record fetched by the user will look highly structured:

{
  "document_id": "doc_98765_etf_marketing",
  "status": "COMPLETED",
  "compliance_score": 82,
  "critical_violations_found": 1,
  "findings": [
    {
      "agent_responsible": "FINRA_Specialist_v2",
      "rule_reference": "FINRA Rule 2210 (Communications with the Public)",
      "severity": "CRITICAL",
      "flagged_text": "Our fund guarantees a baseline return of 8.5% regardless of standard market shifts.",
      "remedy_suggestion": "Remove the word 'guarantees'. Replace with balanced risk language indicating that returns vary and past performance does not guarantee future results."
    }
  ]
}

Would you like to drill down into a specific file? I can help you draft the baseline code for app/graph/workflow.py or set up the Supervisor-to-Specialist communication logic. Let me know which component you want to write next.

