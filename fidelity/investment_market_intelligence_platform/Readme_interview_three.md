# Investment & Market Intelligence Platform — Architecture, Request Flow, and Design Patterns

Your project is best understood as a layered application with Hexagonal Architecture (Ports and Adapters), a LangGraph workflow, and repository-based persistence.

I'll walk through it as if we're following one real request through your codebase—from the moment a user submits a financial research question until the API returns a response.

I'll cover three things:

1. Architecture: what each layer and module does, and why it exists.

2. End-to-end execution: a sample API request, the internal calls, database operations, graph execution, and final response.

3. Design patterns: which patterns your code uses, where they appear, and how they improve the design.

One important distinction: your current project contains a working architectural foundation, but some integrations are scaffolds. I'll identify what the code does today versus what you would add for a production deployment. That distinction will help you explain the project confidently in a Senior or Staff AI Engineer interview.

# 1. The architecture at a glance

Client / Financial Research Analyst

Submits a research request and reads the report

API Layer — FastAPI

Routes · Pydantic schemas · Dependencies · Authentication boundary

Application Layer

ReviewService · Use cases · Workflow coordination

Domain Layer

Review · Evidence · ReviewStatus · Business rules

Ports and Adapters

Repository interfaces · ResearchWorkflow · ChatModel · MarketDataProvider

PostgreSQL

Reviews · Evidence · pgvector schema

LangGraph

Retrieve → Analyze

Providers

LLM · Market data

Background processing extension

Celery + Redis are present as integration points. The current review flow runs inline; it is not yet dispatched to a Celery worker.

The key architectural idea is that the API does not need to know how the LLM works, and the business logic does not need to know how PostgreSQL works. Those details sit behind interfaces.

## The main layers

| Layer       | Main responsibility                              | Representative project modules        |
| ----------- | ------------------------------------------------ | ------------------------------------- |
| API         | HTTP, request validation, response serialization | `app/api/routes.py`                   |
| Application | Coordinates use cases                            | `app/application/use_cases.py`        |
| Ports       | Defines required capabilities                    | `app/application/ports.py`            |
| Domain      | Business concepts and rules                      | `app/domain/models.py`, `policies.py` |
| Workflow    | Orchestrates AI processing                       | `app/agents/graph.py`                 |
| Tools       | Gives the workflow controlled capabilities       | `app/agents/tools.py`                 |
| Adapters    | Implements external capabilities                 | `app/adapters/`                       |
| Persistence | Stores application data                          | `app/db/`                             |
| Workers     | Background task integration                      | `app/workers/tasks.py`                |
| Core        | Shared configuration and infrastructure concerns | `app/core/`                           |

The exact responsibility of a module matters more than its folder name. In an interview, explain what it owns, what it depends on, and what it must not depend on.

# 2. Sample business scenario

Imagine a financial research analyst wants to investigate a company.

Example request

“Analyze the key business and investment risks for Company ABC. Use the available research evidence and return a structured report with supporting sources.”

This is an illustrative request. The company and report below are examples, not live financial research or investment advice.

The client sends a request to the review-creation endpoint. The API validates it, the application creates a review, and the research workflow retrieves evidence and generates an analysis.

The important point is that this is not one giant function. It is a chain of components, each with a clear responsibility.


# 3. Step-by-step: from HTTP request to HTTP response

## Step 1 — The client sends a request

The analyst sends an HTTP `POST` request to the review endpoint.

Illustrative request:

http

```
POST /reviews
Content-Type: application/json
Authorization: Bearer <access-token>
```

JSON

```
{
  "company": "Company ABC",
  "research_question": "Analyze the key business and investment risks",
  "tenant_id": "tenant-123"
}
```

The exact field names should follow your project's request schema; this payload illustrates the business flow.

At this point, the request is still untrusted input. The system must validate its structure and derive the authenticated user's identity and tenant context from trusted authentication data, not blindly trust a tenant ID supplied by the client.

## Step 2 — FastAPI receives the request

The request enters through `app/api/routes.py`.

The API layer is responsible for HTTP concerns:

* Matching the URL and HTTP method to a route.

* Validating the request using the relevant schema.

* Resolving dependencies.

* Calling the application use case.

* Converting the result into an HTTP response.

Conceptually, the route does something like this:

Python

Run

```
@router.post("/reviews")
async def create_review(
    request: CreateReviewRequest,
    service: ReviewService = Depends(get_review_service),
):
    return await service.create(request)
```

This is an illustrative example of the pattern, not a verbatim replacement for your route implementation.

### Why keep the route thin?

The route should not contain SQL queries, prompts, retrieval logic, or the entire AI workflow.

If business logic lives in the route, it becomes difficult to reuse it from a Celery worker, test it independently, or expose it through another interface.

The route acts as an HTTP adapter: it translates an HTTP request into an application-level operation.

## Step 3 — Request validation happens

FastAPI and Pydantic validate the incoming request against the defined schema.

For example, validation can check:

* Required fields are present.

* Strings have acceptable lengths.

* Fields have the correct types.

* Enumerated values are valid.

* Nested structures have the expected shape.

If the request is malformed, the API returns a client error, typically HTTP `422` for request validation.

The workflow should not start when the request fails validation.

Staff-level consideration: schema validation is not authorization. A syntactically valid `tenant_id` does not prove that the caller is allowed to access that tenant.

## Step 4 — The application use case takes over

The route invokes the application layer, primarily `ReviewService` in `app/application/use_cases.py`.

This is where the business operation is coordinated.

The current `ReviewService.create()` flow broadly does the following:

1. Validates the request according to application rules.

2. Creates a review record.

3. Saves the record through the repository.

4. Marks the review as running.

5. Invokes the research workflow.

6. Stores the generated report, or records a failure.

This is the central orchestration point for the use case.

The application layer knows what needs to happen, but it should not need to know the SQL statements used to persist a review or the vendor-specific API used to call a model.

### Why not put this logic in the graph?

The graph is responsible for AI workflow execution. The application service is responsible for the broader business use case.

For example, creating a review, enforcing a review's lifecycle, persisting its status, and deciding what the API returns are application responsibilities. Retrieving evidence and generating analysis are workflow responsibilities.

This separation keeps the AI framework from becoming the entire application architecture.

## Step 5 — The application calls repository ports

The application needs to persist and retrieve data. It does so through interfaces defined in `app/application/ports.py`.

For example, a repository port might conceptually look like this:

Python

Run

```
from typing import Protocol

class ReviewRepository(Protocol):
    async def save(self, review):
        ...

    async def get_by_id(self, review_id, tenant_id):
        ...
```

The actual project interface may have different method signatures; this illustrates the design.

The important detail is that `ReviewService` depends on the contract, not directly on a SQLAlchemy implementation.

The dependency direction is:

`ReviewService → ReviewRepository interface ← PostgreSQL adapter`

The PostgreSQL adapter implements the interface. Dependency injection supplies that adapter to the application.

### What happens in PostgreSQL?

The persistence layer stores review information such as its identifier, tenant, status, and report data, depending on the mapped model and schema.

The project has SQLAlchemy persistence models, including review and evidence records. It also defines a pgvector column for evidence embeddings.

That vector column provides a place to store embeddings, but it does not by itself mean that every stage of a production ingestion pipeline is already implemented.

## Step 6 — The application invokes the research workflow

Once the review has been prepared, the application invokes the workflow through its workflow port.

Conceptually:

Python

Run

```
report = await research_workflow.run(review)
```

The actual method and arguments should match the project's port.

This interface allows the application to invoke a research workflow without depending directly on the details of LangGraph.

That gives you an important extension point: the workflow could later be replaced or expanded while the review use case remains mostly unchanged.

# 4. Inside LangGraph: retrieval and analysis

Your current graph has two principal nodes:

1. `retrieve_evidence`

2. `research_and_risk`

The graph is sequential in the current implementation.

## Step 7 — The retrieval node runs

The graph's retrieval node calls the research tool exposed through `app/agents/tools.py`.

The tool is responsible for obtaining relevant evidence and returning it in a structured form.

Conceptually:

Python

Run

```
async def retrieve_evidence(state):
    result = await research_tools.search_evidence(
        tenant_id=state.tenant_id,
        query=state.research_question,
    )

    return {"evidence": result}
```

This is illustrative pseudocode, not a literal copy of your graph node.

### What should happen in a production retrieval tool?

A complete implementation would:

1. Validate the query and trusted tenant context.

2. Apply access-control filters.

3. Search permitted evidence.

4. Rank or rerank candidate passages.

5. Return source metadata and relevant text.

6. Preserve provenance for the final report.

Your project has a `ResearchTools.search_evidence()` abstraction that accepts tenant and query information and returns a structured result. The completeness of the underlying retrieval strategy depends on the configured repository and implementation.

### Why expose retrieval as a tool?

The tool creates a controlled boundary between the graph and the retrieval implementation.

The graph does not need to know how the evidence repository executes its queries. It asks for evidence using a defined interface and receives a structured result.

This also makes the retrieval behavior easier to test independently.

## Step 8 — The research and risk node runs

After retrieval, LangGraph passes the updated state to the `research_and_risk` node.

That node uses the available evidence and the configured chat-model adapter to produce an analysis.

Conceptually:

Python

Run

```
async def research_and_risk(state):
    report = await chat_model.generate(
        question=state.research_question,
        evidence=state.evidence,
    )

    return {"report": report}
```

Again, this is a simplified illustration of the execution concept.

The output should be validated before the application treats it as a usable report. For example, the application should check required fields, evidence references, and permitted status transitions.

### What does the LLM adapter do?

Your project defines a `ChatModel` abstraction and includes a `MockChatModel`.

The mock returns illustrative output for development and testing. It is not the same as a live OpenAI or other production model integration.

The benefit of the abstraction is that a real provider adapter can be introduced without embedding provider-specific SDK calls throughout the graph and application.

## Step 9 — LangGraph returns the workflow result

Once the two nodes finish, the graph reaches its end state and returns the workflow output.

The current graph can be summarized as:

Input state

Research question · Tenant context

Node 1: Retrieve evidence

Research tool → evidence result

Node 2: Research and risk

Chat model → structured analysis

Final graph state

Evidence + generated report

A subtle but important point: LangGraph manages the workflow's state and transitions. It does not automatically make the workflow a multi-agent system, nor does merely accepting a checkpointer parameter guarantee that durable checkpointing and human resume are fully configured.

# 5. Back to the application: persistence and response

## Step 10 — The report is persisted

The application receives the graph's output and stores it through the review repository.

The review is then moved to the appropriate status based on the workflow outcome and the application's rules.

For example, the application may record:

* Review ID.

* Tenant ID.

* Current status.

* Generated report.

* Error details, if processing failed.

* Relevant timestamps.

The exact fields depend on the project's ORM model and report schema.

A production design should make the report persistence and status transition consistent. If the workflow succeeds but the database update fails, the system needs a recovery strategy rather than reporting success prematurely.

## Step 11 — The API serializes the response

The application returns the result to the route. The route serializes it according to the response schema.

An illustrative successful response could look like this:

JSON

```
{
  "review_id": "rev-8f31",
  "status": "completed",
  "report": {
    "summary": "Illustrative research summary",
    "key_risks": [
      {
        "category": "business",
        "finding": "Illustrative business risk",
        "evidence_ids": ["evidence-101"]
      },
      {
        "category": "market",
        "finding": "Illustrative market risk",
        "evidence_ids": ["evidence-205"]
      }
    ]
  }
}
```

This is an example of the response shape, not a claim that these exact fields or values are returned by your current schema.

If the current request is processed synchronously, the client waits for the workflow to finish before receiving the final response. That is the current architectural limitation.

For long-running production workflows, I would return a job or review identifier promptly and let the client retrieve the result later.

## Step 12 — What if the request fails?

The system needs distinct handling for different failure classes.

| Failure                       | Expected handling                                                  |
| ----------------------------- | ------------------------------------------------------------------ |
| Invalid request               | Return a validation error; do not start the workflow               |
| Unauthorized tenant or action | Reject the request                                                 |
| Evidence retrieval failure    | Record a workflow failure or apply a bounded retry                 |
| LLM timeout                   | Retry only if appropriate; otherwise fail safely                   |
| Invalid model output          | Validate, optionally attempt bounded repair, then fail or escalate |
| Database persistence failure  | Do not report durable success; recover safely                      |
| Human review required         | Keep the report pending review until an authorized decision        |

For your current synchronous implementation, a workflow failure is recorded by the application. In a production asynchronous design, the same failure would be reflected in the persisted job state and exposed through a status endpoint.

# 6. The design patterns involved

Now let's connect the architecture to the actual patterns. This is one of the most important parts of a Senior/Staff interview: explain not only the pattern's name, but also the problem it solves and its trade-offs.

## Pattern 1 — Hexagonal Architecture (Ports and Adapters)

Core architectural pattern

Where: `app/application/ports.py`, `app/adapters/`, and the application use cases.

The application defines what it needs. Infrastructure provides implementations.

For example:

* The application needs to save a review.

* `ReviewRepository` defines that capability.

* A PostgreSQL-backed repository implements it.

* Dependency injection supplies that implementation to `ReviewService`.

The same principle applies to `ChatModel`, `ResearchWorkflow`, and `MarketDataProvider`.

Why use it?

* Infrastructure can be replaced independently.

* Business logic can be tested without external systems.

* Provider-specific details do not leak throughout the codebase.

* The system can support different implementations of the same capability.

Trade-off: more interfaces and wiring. For a tiny application, that can be unnecessary overhead. Here, the number of external systems and the need for testing make the boundary useful.

## Pattern 2 — Repository Pattern

Persistence abstraction

Where: Repository contracts in `app/application/ports.py` and their persistence implementations.

A repository gives the application a business-oriented interface for data access.

Instead of spreading SQLAlchemy queries through route handlers and workflow nodes, the application calls methods that represent persistence operations.

For example:

Python

Run

```
review = await review_repository.get_by_id(
    review_id=review_id,
    tenant_id=tenant_id,
)
```

The repository is responsible for implementing that operation against the database.

Why use it?

It centralizes query behavior, makes tenant-scoped access easier to enforce consistently, and allows tests to substitute an in-memory or fake repository.

Trade-off: avoid a generic repository with dozens of methods that merely wrap ORM calls. A good repository exposes operations that make sense for the application.

## Pattern 3 — Dependency Injection (DI)

Composition and testing

Where: FastAPI dependencies and application service construction.

The application receives its dependencies rather than constructing concrete infrastructure objects internally.

For example, `ReviewService` receives:

* A review repository.

* The research workflow.

* Any other required application dependencies.

This makes it possible to provide a mock workflow in a unit test and a real workflow in a deployed environment.

Why use it?

It reduces tight coupling, improves testability, and keeps configuration in one place.

Trade-off: the dependency graph can become difficult to understand if every object is injected through many layers. Keep the graph explicit and avoid unnecessary abstractions.

## Pattern 4 — Adapter Pattern

External integration boundary

Where: `app/adapters/`, including the LLM and market-data integrations.

An adapter translates between the application's internal contract and an external system's API or data format.

For example, a future production LLM adapter would translate your application's `ChatModel` request into a provider SDK request, then normalize the provider's response into the format expected by the application.

Similarly, a market-data adapter would normalize a vendor's response into a common domain representation.

Why use it?

It isolates vendor-specific code, makes provider replacement easier, and prevents external data formats from spreading through the domain.

Trade-off: a common interface should represent capabilities that providers genuinely share. Don't force every provider into a lowest-common-denominator abstraction that hides important differences.

## Pattern 5 — Strategy Pattern

Supported extension point

Where: The interchangeable capability interfaces, particularly model and market-data providers.

The Strategy pattern lets the application select between implementations of a capability.

For example, an application might use:

* A mock chat model for tests.

* A production chat model for deployed workloads.

* Different approved market-data providers depending on configuration.

The caller uses the same interface while the implementation varies.

Your project establishes these extension points. The existence of an interface does not mean that multiple production strategies are already implemented.

Why use it?

It allows provider selection and substitution without rewriting business logic.

Trade-off: selecting a strategy requires explicit configuration, compatibility checks, and often provider-specific error handling.

## Pattern 6 — Workflow / State Machine

AI orchestration pattern

Where: `app/agents/graph.py` and the review lifecycle.

LangGraph models the AI workflow as nodes connected by transitions.

The current research workflow is a sequential graph. Separately, the review lifecycle has statuses and decisions managed by the application.

These are related but distinct state machines:

* Workflow state: which AI processing step is executing.

* Business state: whether the review is running, awaiting review, completed, or failed.

Keeping those concepts separate helps avoid confusing “the graph finished” with “the review is approved.”

Why use it?

It makes execution explicit and creates a foundation for conditional paths, checkpoints, retries, and human review.

Trade-off: graph complexity can grow rapidly. I would keep the workflow as simple as possible and add nodes when they represent a meaningful step or control boundary.

## Pattern 7 — Tool Abstraction

Controlled capability boundary

Where: `app/agents/tools.py`.

The graph invokes a research capability through a tool abstraction rather than embedding all retrieval logic directly into the graph node.

This is similar to the Command/Facade family of ideas: the caller invokes a defined operation without needing to know its internal implementation.

The tool should validate its inputs, enforce access restrictions, constrain the amount of work, and return a predictable result.

Why use it?

It creates a clear boundary for authorization, testing, and observability.

Trade-off: calling something a “tool” does not make it safe. Tool-level authorization and argument validation must still be implemented.

## Pattern 8 — DTO / Data Transfer Object

Where: API request and response schemas.

DTOs define the data contract crossing a boundary.

The request schema validates client input; the response schema controls what is returned. These schemas should not expose internal ORM objects or sensitive fields accidentally.

Why use it?

It decouples the API contract from database storage and internal domain representations.

Trade-off: mappings between API, domain, and persistence models introduce some duplication. That is acceptable when it protects important boundaries.

## Pattern 9 — Dependency Inversion Principle

Where: The overall application-to-port relationship.

Dependency Inversion is a SOLID principle, not a separate object-creation pattern.

High-level application logic depends on abstractions rather than concrete infrastructure details. The database adapter and LLM adapter implement those abstractions.

This is closely related to Hexagonal Architecture, but the two terms are not identical: Hexagonal Architecture is an overall architectural style, while Dependency Inversion is a principle that helps achieve it.

## Pattern 10 — Idempotency / Deduplication

Foundation present; enforcement needed

Where: `app/services/idempotency.py`.

The project computes a request fingerprint from a canonicalized payload and tenant context.

That fingerprint can identify equivalent requests, but it does not by itself prevent duplicate processing.

To complete the pattern, I would persist the idempotency key or fingerprint, enforce uniqueness in the database, define duplicate-request behavior, and make background processing safe to repeat.

This is especially important when retries, timeouts, and message redelivery are involved.

# 7. How the patterns work together

The patterns are not independent decorations. They form a connected design.

FastAPI route + DTO

Receives and validates the external request.

Application use case + DI

Coordinates the business operation using injected dependencies.

Ports + adapters + repositories

Connect business logic to persistence, the LLM, and market-data providers.

LangGraph workflow + tools

Executes the research steps and returns structured results.

Persistence + business state

Stores the review, report, and lifecycle status.

For example, if you replace the mock model with a production provider, the Adapter and Strategy extension points help contain the change. If you replace PostgreSQL persistence, the Repository and Port boundaries contain much of that change. If you add a new workflow node, the graph changes without requiring the API route to understand its internal steps.

That is the architectural payoff.

# 8. What I would change before calling this production-ready

The architecture is a reasonable foundation, but the following are the major improvements I would prioritize.

| Area            | Current project                        | Production improvement                                          |
| --------------- | -------------------------------------- | --------------------------------------------------------------- |
| LLM             | Mock adapter                           | Approved provider adapter, timeouts, retries, structured output |
| Workflow        | Two sequential nodes                   | Explicit routing only where needed; bounded execution           |
| Handoffs        | Routing concepts                       | Real specialist nodes and validated transitions                 |
| Retrieval       | Evidence abstraction and vector schema | Verified end-to-end ingestion, embedding, filtering, ranking    |
| Background work | Celery scaffold                        | Dispatch review jobs through Celery                             |
| HITL            | Application-level reviewer decisions   | Durable graph interrupt, checkpoint, and resume                 |
| Idempotency     | Request fingerprint                    | Persisted key, uniqueness constraint, duplicate handling        |
| Security        | Authorization logic foundations        | End-to-end tenant isolation and security tests                  |
| Operations      | Infrastructure foundations             | Tracing, metrics, alerting, evaluation, recovery tests          |

One more architectural improvement: when connecting Celery, I would use a transactional outbox or another reliable dispatch mechanism. Otherwise, the database may record a review while publishing its task to Redis fails, leaving the review stuck.

# 9. Your interview-ready explanation

Here is a concise version you can deliver when the interviewer says, “Walk me through the architecture and design patterns.”

> “The platform uses a layered architecture with Hexagonal Architecture principles. FastAPI handles the HTTP boundary and request validation. The application layer coordinates the review use case, while the domain layer represents reviews, evidence, and business rules.
>
> The application depends on ports for persistence, the research workflow, the chat model, and market-data access. Infrastructure adapters implement those contracts, and dependency injection provides the concrete implementations. This keeps business logic independent of SQLAlchemy and provider-specific SDKs.
>
> When a research request arrives, the API validates it and calls the review service. The service creates and persists the review, then invokes the LangGraph workflow. The current graph has two sequential steps: retrieving evidence through a research tool, followed by research and risk analysis using the configured chat-model adapter. The service then persists the result or records a failure and returns the API response.
>
> The key patterns are Ports and Adapters, Repository, Dependency Injection, Adapter, Strategy-style provider substitution, DTOs, and explicit workflow/state management. These patterns improve testability, replaceability, and separation of concerns.
>
> I would be transparent that the current LLM is mocked, the graph is not yet a full multi-agent system, and the review workflow currently runs inline despite the Celery scaffold. My production roadmap would complete the provider integrations, end-to-end RAG pipeline, asynchronous execution, durable HITL, idempotency, and tenant-isolation testing.”

The most important point: be able to draw the request flow, name the actual module responsible for each step, and explain what happens when that step fails. That demonstrates architectural understanding much more convincingly than simply listing frameworks or design-pattern names.
