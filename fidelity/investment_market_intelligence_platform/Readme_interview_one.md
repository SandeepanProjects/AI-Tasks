# Investment Market Intelligence Platform — Complete Interview Guide

Your uploaded project is an Investment Market Intelligence Platform. Its purpose is to help users research financial assets, retrieve supporting market evidence, analyze risks, and produce a structured research report with source references and limitations.

I'll explain it from the perspective of a Senior AI Engineer or Staff AI Engineer interview: the business problem, architecture, end-to-end execution, every major component, design patterns, technology choices, alternatives, and the limitations you should be prepared to discuss.

One important distinction: your ZIP is a reference scaffold, not yet a fully operational production investment platform. It contains the architectural foundations for asynchronous processing, market-data integration, vector retrieval, and human review, but some of those integrations are currently stubs or are not wired into the main workflow. Being able to explain that distinction accurately will strengthen your interview discussion.

## 1. How to introduce the project to an interviewer

2-minute project pitch

"I designed an Investment Market Intelligence Platform that helps financial research teams analyze investment-related questions using source-backed evidence.

The platform follows a layered, hexagonal architecture. FastAPI provides the API layer, PostgreSQL stores reviews and evidence, and pgvector supports semantic retrieval. LangGraph orchestrates the research workflow, while typed tools provide controlled access to evidence. The LLM generates a structured research report containing observations, risks, evidence references, and limitations.

I separated the domain and application logic from infrastructure through ports and adapters. This allows the model provider, market-data provider, and persistence implementation to be changed without rewriting the business use cases.

Since investment research is a sensitive domain, I designed explicit controls around tenant isolation, role-based access, evidence provenance, output validation, and human review. The model generates a draft analysis; it does not execute trades or make investment transactions.

The key engineering challenge is combining probabilistic AI analysis with deterministic controls, traceable evidence, and a workflow that can be tested and operated reliably."

Copy project pitch

### If the interviewer asks, "What does it actually do?"

Explain the flow with a concrete example:

A user asks, "Analyze the risk factors associated with Bitcoin over the last 90 days."

1. The API validates the request and identifies the authenticated user and tenant.

2. The application creates a research review.

3. The workflow retrieves relevant evidence for the research question.

4. The model produces a structured analysis containing observations, risks, citations, and limitations.

5. The application validates the report.

6. The report is stored and, when configured, awaits a human reviewer's decision.

The important qualification is that the current market-data provider is unconfigured, the model adapter is a mock, and the main review workflow runs inline. So this describes the intended system behavior, not a claim that the ZIP currently fetches live prices or runs a production Celery-based research pipeline.

# 2. Architecture: how the system is organized

The project combines three architectural ideas:

* Hexagonal architecture (Ports and Adapters): separates business logic from external technologies.

* Layered architecture: separates API, application, domain, and infrastructure responsibilities.

* Graph-based orchestration: uses LangGraph to define the sequence of AI workflow steps.

These are complementary, not competing architectures.

## High-level architecture diagram

Research analyst / reviewer

Submits a question, checks a report, makes a review decision

FastAPI — API / control plane

Routes · Pydantic schemas · JWT · RBAC · dependency injection

Application layer

ReviewService · validation · lifecycle · use cases

LangGraph research workflow

Retrieve evidence

Research & risk analysis

Typed tools · Structured model output · Report validation

PostgreSQL

Reviews, evidence, vectors

Review controls

Authorization, audit, approval state

Infrastructure adapters: model provider, licensed market-data provider, database repositories

The diagram shows the logical architecture. In the current implementation, the review service invokes the workflow directly rather than dispatching the research through Celery. Also, the graph currently has two sequential nodes, not a fully implemented multi-agent network.

## 3. Why did you follow hexagonal architecture?

Hexagonal architecture is also called Ports and Adapters. Its central idea is that your business logic should not be tightly coupled to a particular database, model vendor, or external API.

For example, your application defines contracts such as:

* `ReviewRepository`

* `EvidenceRepository`

* `ResearchWorkflow`

Concrete infrastructure implements those contracts. The application can use a PostgreSQL repository today and a different persistence adapter in a test or future deployment without changing the business use case.

Ports — interfaces

Define what the application needs, without prescribing how the capability is implemented.

Adapters — implementations

Connect the application to SQLAlchemy, PostgreSQL, model SDKs, and external data providers.

### Why not put everything in FastAPI routes?

Because routes should handle HTTP concerns, not own business workflows.

If retrieval, authorization, model invocation, and database writes all live inside one endpoint, the code becomes difficult to test independently. It also becomes harder to expose the same use case through a background worker or another interface.

### Why not use pure Clean Architecture instead?

Hexagonal architecture and Clean Architecture share the same dependency direction. You could implement this project using either approach.

I would describe the actual project as hexagonal architecture with layered separation, rather than claiming that it implements every aspect of a strict Clean Architecture template.


# 4. Every major component and why it exists

Your repository is organized into `api`, `application`, `domain`, `agents`, `adapters`, `db`, `services`, `workers`, and `core`. Here is how I would explain each folder during a code walkthrough.

## 4.1 API layer — `app/api/`

Files: `routes.py`, `dependencies.py`

Responsibility: Accept HTTP requests, authenticate users, validate input, call the application service, and return API responses.

The project exposes endpoints to create a review, retrieve a review, and submit a review decision.

The route uses FastAPI's `Depends()` mechanism to obtain the authenticated principal and `ReviewService`. Pydantic schemas define the request and response shapes.

Why FastAPI?

* Async support fits I/O-heavy database and model interactions.

* Pydantic provides structured request validation.

* Dependency injection makes authentication and service dependencies testable.

* OpenAPI documentation is generated automatically.

Why not Flask? Flask can implement the same API, but FastAPI gives this project native async endpoint support and integrated type-driven validation.

Why not Django REST Framework? DRF is a strong choice for applications needing Django's broader ORM, admin, and batteries-included ecosystem. This project uses a more modular service architecture, so FastAPI is a natural fit.

Senior-level point: FastAPI does not make the entire application non-blocking automatically. Blocking SDK calls or synchronous database operations can still stall execution. Every external dependency needs appropriate async handling or thread/process isolation.

## 4.2 Application layer — `app/application/`

Files: `use_cases.py`, `ports.py`, `schemas.py`

Responsibility: Implement application use cases and coordinate domain objects with infrastructure.

The main class is `ReviewService`. It handles review creation, retrieval, and reviewer decisions.

The application layer also defines protocols for repositories and the research workflow. Those protocols are the ports through which the application communicates with its dependencies.

Why use a service/use-case layer?

It makes the business operation reusable without requiring an HTTP request. A future CLI, scheduled process, or properly implemented Celery task could invoke the same application operation.

Why not put business logic in the ORM models?

The ORM model represents persisted data. The application service coordinates the complete use case, including authorization, workflow invocation, and persistence. Keeping those responsibilities separate avoids turning database models into oversized service objects.

## 4.3 Domain layer — `app/domain/`

Files: `models.py`, `policies.py`

Responsibility: Define business concepts and enforce domain rules.

The important domain models are:

* `Review`: the research request, tenant, status, report, and reviewer information.

* `Evidence`: a source item with provenance, observation time, content, and content hash.

* `ReviewStatus`: the review lifecycle states.

The domain policies validate the research request and generated report. For example, the request has limits on question length, asset count, and lookback period.

Why separate domain models from SQLAlchemy models?

A domain object represents the business concept. A SQLAlchemy row represents its database storage. Separating them reduces ORM coupling and makes core business behavior easier to test.

Why not use Pydantic models for everything?

Pydantic is excellent for parsing and validating external data. Dataclasses and enums are also useful for internal domain objects because they are lightweight and do not require the domain to depend on an API-validation framework.

There is no universal requirement to separate them; the key is to choose a consistent boundary.

## 4.4 Agent layer — `app/agents/`

Files: `graph.py`, `tools.py`, `handoffs.py`

Responsibility: Define the research workflow, controlled evidence tools, and routing decisions.

### `graph.py` — LangGraph workflow

The graph has two nodes:

1. `retrieve_evidence`

2. `research_and_risk`

The retrieval node calls the evidence tool and stores the evidence in graph state. The analysis node sends the question, assets, lookback period, and retrieved evidence to the model. The report is validated before being returned.

The edges are sequential: retrieval → analysis → end.

Why LangGraph?

It represents workflow state and transitions explicitly. It supports more complex branching, loops, checkpointing, and interrupts when those are implemented and configured.

Why not a plain Python function?

For a two-step workflow, a plain function would be simpler. LangGraph becomes more valuable as the workflow grows to include conditional routing, specialist agents, retries, and durable human-interaction steps.

That is a trade-off worth acknowledging: the current graph is simple enough that LangGraph is an architectural foundation for future orchestration, rather than proof of a sophisticated multi-agent system.

### `tools.py` — controlled tool access

The `ResearchTools` class exposes a specific `search_evidence()` capability. It accepts a tenant ID and query, asks the evidence repository for a bounded number of results, and returns a structured `ToolResult`.

Why explicit tools instead of arbitrary model-generated tool execution?

An allowlist limits what the model-driven workflow can request. The tool does not accept arbitrary SQL or arbitrary URLs. This reduces the attack surface and makes permissions and auditing easier to enforce.

### `handoffs.py` — routing policy

The project defines possible handoff targets such as research, portfolio risk, evidence review, and human review. Routing is currently based on deterministic keyword checks.

Be precise in the interview: these are defined routing targets, but the current graph does not actually dispatch to separate nodes for each of them. `choose_handoff()` populates a route list; it does not yet create a full multi-agent handoff workflow.

## 4.5 Adapter layer — `app/adapters/`

This folder isolates external dependencies.

| File             | Purpose                                                     |
| ---------------- | ----------------------------------------------------------- |
| `llm.py`         | Defines the chat-model contract and a mock implementation   |
| `market_data.py` | Defines market observation types and the provider interface |
| `in_memory.py`   | Provides an in-memory adapter for development or testing    |

The model interface accepts a system prompt, user input, and schema, then returns a structured dictionary. The current `MockChatModel` returns illustrative fixture output rather than calling a live LLM.

The market-data adapter defines fields such as symbol, price, currency, observation timestamp, provider, delay status, and methodology. The default implementation fails closed because no licensed provider is configured.

Why use adapters?

The rest of the application can depend on stable interfaces instead of importing vendor SDKs everywhere.

Why not call the OpenAI SDK directly inside the graph?

That would couple workflow code to one provider. The adapter gives us a place to handle provider-specific response formats, timeouts, errors, and model configuration.

## 4.6 Database layer — `app/db/`

Files: `models.py`, `session.py`, `rls.sql`

Responsibility: Database mappings, session management, vector columns, and tenant isolation controls.

The SQLAlchemy models include:

* `ReviewRow` — stores the research request, status, report, and reviewer fields.

* `EvidenceChunkRow` — stores evidence content, provenance, tenant ID, and an embedding vector.

The embedding column is declared as `Vector(384)`, so the embedding model used to populate it must produce vectors with exactly 384 dimensions.

Why PostgreSQL?

It provides transactional persistence, relational constraints, indexing, and a mature operational ecosystem.

Why pgvector?

It allows vector similarity search alongside relational metadata. This is useful when evidence must be filtered by tenant, source, or observation time.

Why not store everything in a vector database?

Reviews, reviewer decisions, and audit records have relational and transactional requirements. A vector database alone would not replace the need for a transactional system of record.

Important distinction: The project defines vector storage, but that alone does not demonstrate that embeddings are being generated, persisted, and searched end to end. You need a working ingestion and retrieval implementation to claim a complete production RAG pipeline.

## 4.7 Worker layer — `app/workers/`

The project includes a Celery application and an `ingest_source` task. That task currently validates the required identifiers and returns a stub response; it does not fetch or ingest external market data.

Why Celery?

For a production system, ingestion and research analysis can take longer than a typical HTTP request. Celery allows workers to run independently, use a broker, retry selected failures, and scale separately.

Why not FastAPI BackgroundTasks?

BackgroundTasks is useful for small, process-local tasks. Celery is better suited to durable distributed processing with independent workers and broker-based delivery.

But in this ZIP, the review creation use case calls the workflow inline. So Celery is present, but it is not yet the execution mechanism for research review creation.

## 4.8 Core and supporting services

| Component                          | Why it exists                                             |
| ---------------------------------- | --------------------------------------------------------- |
| `app/core/config.py`               | Centralized configuration and environment-driven settings |
| `app/core/security.py`             | Principal, role, and authentication-related logic         |
| `app/core/errors.py`               | Consistent domain/application error types                 |
| `app/core/logging.py`              | Logging configuration                                     |
| `app/services/audit.py`            | Audit-related service boundary                            |
| `app/services/idempotency.py`      | Request fingerprinting for duplicate detection            |
| `migrations/`                      | Versioned database schema changes                         |
| `tests/`                           | Automated tests                                           |
| `Dockerfile`, `docker-compose.yml` | Container packaging and local service orchestration       |

The `request_fingerprint()` function computes a stable SHA-256 fingerprint from a canonicalized payload and tenant ID. That is a useful building block for idempotency, but a fingerprint alone does not prevent duplicate operations; it must be stored and enforced through a persistence constraint or equivalent mechanism.

# 5. The design patterns you should explain

Your project uses a combination of explicit software patterns and architectural patterns. Explain the pattern only where it solves a real problem.

| Pattern                 | Where it appears                                   | Why it is useful                                |
| ----------------------- | -------------------------------------------------- | ----------------------------------------------- |
| Ports and Adapters      | `application/ports.py`, `adapters/`                | Decouples business logic from infrastructure    |
| Repository              | `ReviewRepository`, `EvidenceRepository` contracts | Separates persistence operations from use cases |
| Dependency Injection    | FastAPI dependencies and service construction      | Makes components replaceable and testable       |
| Strategy / Polymorphism | `ChatModel`, `MarketDataProvider` protocols        | Allows alternative provider implementations     |
| State Machine           | `ReviewStatus` and decision transitions            | Makes lifecycle states explicit                 |
| Workflow Orchestration  | LangGraph `StateGraph`                             | Makes execution steps and transitions explicit  |
| Adapter                 | Model and market-data integrations                 | Isolates vendor-specific APIs                   |
| Fail-closed             | Unconfigured market-data provider                  | Avoids fabricating financial observations       |

The ports and adapter contracts are visible in the application interfaces and external integration modules.

### Strategy versus Adapter — a common interview trap

These patterns are related but solve different problems.

* Adapter: translates one external interface into the interface expected by the application.

* Strategy: lets the application choose among interchangeable implementations of a behavior.

For example, wrapping a vendor's market-data SDK is an Adapter. Supporting multiple market-data retrieval algorithms behind a common interface is Strategy.

A protocol by itself is not the entire Strategy pattern. You also need interchangeable implementations and a way to select one.

### Is this event-driven architecture?

Not fully. Celery provides an asynchronous task mechanism, and it is appropriate for an event-driven extension. But the primary review flow in this scaffold is currently synchronous within the application service. I would call it a layered application with a graph workflow and a Celery-based ingestion foundation, not a fully event-driven architecture.


# 6. Why these technologies instead of alternatives?

This is where interviewers often probe whether you understand the technology or merely followed a tutorial.

## Technology decision matrix

| Technology chosen      | Why it fits                                 | Alternative and when I'd choose it                                                 |
| ---------------------- | ------------------------------------------- | ---------------------------------------------------------------------------------- |
| FastAPI                | Async APIs, Pydantic, dependency injection  | Django REST Framework for a Django-centric platform                                |
| PostgreSQL             | Transactional system of record              | DynamoDB for access patterns that strongly favor key-value/document storage        |
| pgvector               | Relational data and vectors in one database | Qdrant when dedicated vector-search capabilities or independent scaling justify it |
| LangGraph              | Explicit stateful workflow orchestration    | Plain Python for a small, linear workflow                                          |
| Celery                 | Distributed background jobs                 | SQS + workers for an AWS-native queue architecture                                 |
| Redis                  | Low-latency broker/backend capabilities     | RabbitMQ for broker-focused routing and delivery needs                             |
| SQLAlchemy             | Python ORM and SQL abstraction              | Direct SQL for a deliberately small, SQL-centric application                       |
| Pydantic               | Typed boundary validation                   | Standard dataclasses for internal objects that do not need parsing or validation   |
| Hexagonal architecture | Infrastructure independence and testability | A simpler layered monolith if the application has very few external dependencies   |

These are conditional trade-offs, not universal rules. For example, Celery and SQS are not perfectly equivalent: Celery is a task-processing framework, whereas SQS is a managed messaging service. They can also be combined in an AWS architecture.

## Why pgvector rather than Qdrant?

For this project, PostgreSQL already owns the review and evidence records. Keeping vectors in the same database reduces infrastructure and simplifies metadata filtering.

I would benchmark pgvector against Qdrant using realistic evidence volume, vector dimensions, filter selectivity, concurrency, and recall requirements. I would move to a dedicated vector database only if the measured benefits justified the added synchronization and operational complexity.

## Why LangGraph rather than LangChain alone?

LangChain provides useful model, prompt, and tool abstractions. LangGraph focuses on stateful execution graphs, conditional transitions, checkpointing, and interruption.

The distinction is not that LangChain cannot build workflows. Rather, LangGraph makes explicit workflow state and execution transitions central to the design.

For the current two-node graph, ordinary Python would also work. The case for LangGraph becomes stronger when the system needs branching, resumable execution, bounded retries, or human approval within the workflow.

## Why not use a fully autonomous agent?

Because the business problem does not require the model to have unrestricted autonomy.

A bounded research workflow is easier to reason about, test, audit, and secure. The application defines which tools are available and what the model is permitted to produce.

In investment research, I would not let a model invent data sources, execute arbitrary code, or place trades. The system should produce a reviewable analysis, not autonomously perform financial transactions.

# 7. Explain the complete execution flow, file by file

An interviewer may ask, "Which function gets called first, and what calls what?"

Here is the current code path.

1. HTTP request

app/api/routes.py · create_review()

2. Application use case

app/application/use_cases.py · ReviewService.create()

3. Request validation

app/domain/policies.py · validate_research_request()

4. Persist review

ReviewRepository · add() / save()

5. Run workflow

ResearchWorkflow · run(review)

6. Retrieve evidence

app/agents/graph.py → ResearchTools.search_evidence()

7. Generate report

ChatModel.structured_completion()

8. Validate report

app/domain/policies.py · validate_report()

9. Persist final state

ReviewService → repository

The route delegates to `ReviewService.create()`. That method validates the request, creates and saves the review, sets its status to running, invokes the workflow, and then stores either the report or a failed status.

### What happens during a reviewer decision?

The decision endpoint calls `ReviewService.decide()`. The service checks whether the caller has the reviewer or admin role, retrieves the review within the caller's tenant, and requires the review to be awaiting review before changing its status.

### What is missing from this execution flow?

Three important production capabilities are not fully wired into the current code:

1. Asynchronous research execution: the review service invokes the graph inline. Celery is currently used for an ingestion stub, not for review processing.

2. True graph-level HITL: the workflow wrapper's `resume()` method does not resume a paused graph. The source explicitly describes a post-graph approval state instead.

3. Live market-data retrieval: the configured provider fails closed, and the mock model returns illustrative output.

The graph accepts a checkpointer, but the code shown does not itself configure a production checkpointer or implement a LangGraph `interrupt()` / `Command(resume=...)` cycle.

# 8. How I would improve this architecture for production

At Staff level, don't just defend the existing choices. Explain how you would evolve them.

P0

Replace mock integrations

Integrate a real, licensed market-data provider and a production LLM adapter. Enforce timeouts, token limits, provider error handling, and data freshness checks.

P0

Complete the evidence pipeline

Implement ingestion, chunking, embedding generation, persistence, vector retrieval, source versioning, and evidence-level evaluation.

P0

Make research execution asynchronous

Persist the review and a transactional outbox event, publish the job, and execute it in an idempotent Celery worker.

P0

Implement durable human review

Configure a durable LangGraph checkpointer, interrupt at the review stage, persist the reviewer decision, and resume the same workflow thread.

P1

Harden security and audit

Verify PostgreSQL RLS with the actual application role, implement separation of duties, protect audit events, and add concurrency-safe decision transitions.

P1

Add evaluation and observability

Build a labeled research benchmark, test evidence attribution and hallucination, and monitor latency, queue age, provider freshness, cost, and reviewer overrides.

The project documentation itself identifies the need for idempotent review creation, durable workflow checkpoints, reliable task dispatch, and separate ingestion/inference queues.

## A staff-level explanation of the transactional outbox

Suppose the application saves a review in PostgreSQL, then tries to enqueue a Celery task. If the database commit succeeds but Redis is unavailable, the review exists but no task is queued.

The transactional outbox solves this by saving the review and an outbox event in the same PostgreSQL transaction. A separate publisher sends the event to the broker and marks it as delivered.

The worker must still be idempotent because messages can be delivered more than once. This design improves reliability without claiming exactly-once execution.

## A staff-level explanation of durable HITL

A real human-in-the-loop workflow needs more than a status field.

The graph must stop at a defined approval boundary, persist the state required to resume, and resume using a validated decision from an authorized reviewer. The business review record and graph checkpoint must remain consistent.

I would test this by killing the worker after the interruption, restarting it, submitting a reviewer decision, and verifying that the same workflow resumes without rerunning completed steps unnecessarily.

# 9. Interview questions you should be ready for

Question 1 of 10

Quick revision

## Why hexagonal architecture?

To keep business use cases independent of database, model, and market-data implementations.

PreviousNext

# 10. Your closing statement

If the interviewer asks, "Anything else you want to highlight?", use this:

"My main design objective was to build a controlled, evidence-backed research workflow rather than a chatbot that generates financial opinions. I separated the domain from infrastructure, used explicit contracts for external dependencies, and introduced structured evidence and report validation.

I also recognize the distinction between an architectural scaffold and a production deployment. The next steps are to complete the live integrations, make execution and human review durable, and validate quality and security through end-to-end tests.

That is how I would take this from a reference implementation to an enterprise-grade investment research platform."

The most important interview rule: Never claim that a component is production-ready merely because its folder, interface, or configuration exists. Explain what is implemented, what is stubbed, why the abstraction exists, and what evidence would prove the production behavior. That is the level of precision expected from a senior or staff engineer.
