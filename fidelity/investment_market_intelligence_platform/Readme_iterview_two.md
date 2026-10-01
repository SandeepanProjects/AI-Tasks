# Investment & Market Intelligence Platform — Senior / Staff AI Engineer Interview Preparation

For your `Investment Market Intelligence Platform`, an interviewer can explore much more than RAG or LangGraph. At Senior or Staff level, they will test whether you understand the business problem, architecture, trade-offs, production failure modes, security, scalability, and the engineering decisions behind your implementation.

I’ve organized the interview preparation into 12 areas, with answers you can explain verbally. The answers distinguish between what your current project implements and what you would add for production—this is important because a Staff Engineer should be able to discuss gaps honestly and explain how they would close them.

# 1. Project overview and architecture

## Q1. Explain your project in two minutes.

Answer:

“I designed an Investment and Market Intelligence Platform that helps financial research teams analyze investment-related information, retrieve supporting evidence, assess risks, and produce structured research reports.

The system is built around FastAPI, PostgreSQL with pgvector, and a LangGraph-based research workflow. I use a layered architecture with domain models, application use cases, repository interfaces, and infrastructure adapters.

The API accepts a research request, validates it, and passes it to the application layer. The workflow retrieves relevant evidence and uses an analysis component to generate a structured report. The report is persisted in PostgreSQL and can be reviewed by an authorized human reviewer.

I separated business logic from infrastructure through ports and adapters, so the LLM provider, database implementation, and market-data provider can be replaced without rewriting the core use cases.

The platform also includes Celery and Redis integration points for background processing, although the current review workflow still executes inline. Similarly, the current LLM adapter is a mock, and the graph is a small sequential workflow rather than a fully implemented multi-agent system.

My focus was to establish a maintainable foundation for a financial research platform, with explicit boundaries for evidence, risk analysis, human review, and future production integrations.”

Why this answer works: It explains the value, architecture, flow, and implementation boundaries without claiming capabilities that are not yet implemented.

## Q2. What business problem does the platform solve?

Answer:

Financial research involves collecting information from multiple sources, checking its relevance, understanding risks, and preparing reports that analysts can review.

The platform aims to reduce repetitive research work by:

* Retrieving relevant evidence for a research question.

* Organizing evidence for downstream analysis.

* Producing structured research and risk outputs.

* Preserving the report and its review status.

* Allowing authorized reviewers to approve or reject a report.

The system is designed to assist analysts, not independently make investment decisions or guarantee financial outcomes.

## Q3. Who are the users of this platform?

Answer:

I would define three main user groups:

| User             | Responsibility                                                 |
| ---------------- | -------------------------------------------------------------- |
| Research analyst | Submits research requests and examines generated reports       |
| Reviewer         | Reviews evidence, risk findings, and report quality            |
| Administrator    | Manages access, tenant configuration, and operational policies |

The authorization model should enforce the user's role and tenant boundary at every relevant API and data-access layer.

## Q4. Explain the architecture from a high level.

Answer:

The architecture has five main layers:

API layer

FastAPI · Routes · Request/response schemas · Authentication

Application layer

Use cases · Workflow orchestration · Authorization decisions

Domain layer

Review models · Evidence · Statuses · Business invariants

Ports and adapters

Repositories · LLM · Market data · External integrations

Infrastructure

PostgreSQL/pgvector · Redis · Celery · External providers

The main design principle is that business logic should not depend directly on infrastructure details. The domain and application layers define what the system needs; adapters implement those requirements.

## Q5. Why did you choose this architecture instead of a simple FastAPI application?

Answer:

A simple application with route handlers calling the database and LLM directly would be quicker initially, but it creates tight coupling.

In this project, I wanted to support:

* Replacing an LLM provider without rewriting business logic.

* Testing use cases without a real database or external API.

* Adding background processing without changing the domain model.

* Enforcing consistent authorization and state transitions.

* Growing the system without putting all logic into route handlers.

The additional abstractions have a cost, so I would not introduce a repository, interface, or service for every trivial operation. I would introduce them where they create a meaningful boundary or simplify testing and change.

## Q6. Is this a microservices architecture?

Answer:

“No. I would describe the current implementation as a layered, modular application using hexagonal architecture and a graph-based workflow.

It has logical boundaries between the API, application logic, domain, adapters, and infrastructure, but those boundaries do not automatically make them independent microservices.

I would start with a modular monolith because it is easier to develop, test, deploy, and operate. I would extract a service only when there is a concrete need for independent scaling, deployment, ownership, or fault isolation.”

## Q7. What is the difference between Senior Engineer and Staff Engineer thinking in this project?

Answer:

A Senior Engineer would focus on implementing the workflow correctly, writing reliable APIs, securing the data, and improving performance.

At Staff level, I would additionally focus on system-wide properties:

* Clear ownership and architectural boundaries.

* Failure isolation and recovery.

* Data consistency across API, worker, and database.

* Multi-tenant security.

* Cost and latency budgets.

* Evaluation and release gates for AI behavior.

* Operational ownership, migration strategy, and long-term maintainability.

The distinction is not simply using more technologies. It is making decisions that keep the entire system reliable as the number of users, integrations, and teams grows.

# 2. Architecture and design patterns

## Q8. Which design patterns are used in your project?

Answer:

I would identify the following patterns, while being precise about where they apply.

| Pattern                | How it applies                                              |
| ---------------------- | ----------------------------------------------------------- |
| Hexagonal architecture | Application logic depends on ports; adapters implement them |
| Repository             | Abstracts persistence operations                            |
| Dependency injection   | Supplies repositories, models, and services to use cases    |
| Adapter                | Wraps infrastructure or external provider implementations   |
| Strategy               | Allows interchangeable implementations of a capability      |
| Workflow/state machine | Models research processing and review transitions           |
| DTO                    | Defines API request and response contracts                  |
| Factory/provider       | Can centralize construction of configured implementations   |

I would avoid claiming that every pattern is fully implemented. For example, a `MarketDataProvider` interface supports a Strategy-style extension point, but a production-ready set of interchangeable providers still needs to be implemented and tested.

## Q9. Explain hexagonal architecture.

Answer:

Hexagonal architecture, also called Ports and Adapters, separates the application's core logic from external systems.

A port defines a capability the application needs. An adapter implements that capability.

For example:

* `ReviewRepository` is a port.

* A SQLAlchemy-backed repository is an adapter.

* `ChatModel` is a port.

* An OpenAI-backed or mock model is an adapter.

* `MarketDataProvider` is a port.

* A licensed market-data integration is an adapter.

This makes it possible to test application behavior using fake adapters and to replace infrastructure without rewriting the use case.

## Q10. Why use the Repository pattern when SQLAlchemy already provides an ORM?

Answer:

SQLAlchemy provides database mapping and query capabilities. The Repository pattern provides an application-facing abstraction over persistence.

It lets the application express operations such as `get_review()` or `save_evidence()` without knowing SQLAlchemy session details.

However, I would not hide every database feature behind an overly generic repository. Complex analytical queries, bulk operations, and performance-sensitive access patterns may need specialized repository methods.

## Q11. What is Dependency Injection, and why is it useful?

Answer:

Dependency Injection means a component receives its dependencies rather than constructing them internally.

For example, `ReviewService` receives a review repository and a research workflow. It does not instantiate a database connection or hard-code an LLM client.

This improves:

* Unit testing.

* Provider replacement.

* Configuration management.

* Separation of responsibilities.

* Control over resource lifetimes.

In FastAPI, dependencies can be assembled through `Depends()`. For production, I would ensure that database sessions and clients have appropriate request or application lifetimes.

## Q12. Why not use a Singleton for the database session?

Answer:

A single shared database session is unsafe for concurrent requests because sessions generally represent mutable transactional state.

I would use a long-lived database engine and connection pool, but create a separate session for each request or unit of work.

For async code, I would use an async engine and `AsyncSession`, ensuring that a session is not concurrently shared across independent tasks.

## Q13. Why use domain models instead of Pydantic request models everywhere?

Answer:

API schemas and domain models serve different purposes.

* API schemas define the external contract.

* Domain models represent business concepts and invariants.

* ORM models represent database persistence.

Keeping them separate prevents database-specific details from leaking into the API and avoids making the domain dependent on a particular web framework.

For a small service, some duplication may be unnecessary. I would maintain separate models where they protect meaningful boundaries, not merely for architectural ceremony.

## Q14. How would you prevent circular dependencies?

Answer:

I would enforce a dependency direction:

`API → Application → Domain`

Infrastructure adapters implement ports defined by the application or domain-facing contracts. The domain should not import FastAPI, SQLAlchemy, Celery, or a specific LLM SDK.

I would use package boundaries, static analysis, and architecture tests to detect violations.

# 3. LangGraph, agents, and orchestration

## Q15. Why did you use LangGraph?

Answer:

LangGraph is useful when an AI workflow needs explicit state, conditional routing, retries, checkpoints, or human intervention.

A simple one-shot LLM call would be enough for a single prompt-response interaction. But research workflows often involve multiple steps: retrieving evidence, evaluating it, analyzing risk, and possibly requesting review.

LangGraph makes those steps explicit and gives us a framework for stateful orchestration.

In the current project, the graph is intentionally small: evidence retrieval followed by research and risk analysis. It is not yet a full multi-agent graph.

## Q16. Explain the current graph execution.

Answer:

The current graph has two primary nodes:

1. `retrieve_evidence` calls the research tool and obtains evidence.

2. `research_and_risk` uses the retrieved context to produce the analysis.

The graph connects the first node to the second and then to the end state.

The workflow can be represented as:

Research request

Retrieve evidence

Research and risk analysis

Structured result

The graph is sequential today. Conditional routing and specialist-agent handoffs are extension points, not completed behavior.

## Q17. Is your project a multi-agent system?

Answer:

“I would describe the current version as an agentic workflow foundation rather than a fully realized multi-agent system.

The project contains handoff concepts for research, portfolio risk, evidence review, and human review. However, the current graph does not dispatch to separate specialist nodes for each target. Its main execution path is sequential.

To make it a true multi-agent workflow, I would implement separate specialist nodes with typed inputs and outputs, explicit routing rules, bounded execution, and deterministic aggregation.”

This is a crucial answer: do not claim multiple autonomous agents if the code does not actually execute them.

## Q18. What is the difference between an agent and a workflow?

Answer:

A workflow follows a predefined execution path. An agent can make decisions about which action or tool to use based on its state and instructions.

For example:

* Workflow: retrieve evidence, then analyze, then validate.

* Agent: decide whether to search again, invoke a risk tool, or ask for clarification.

I prefer workflows for high-risk financial operations because their behavior is easier to constrain, test, and audit. I would allow bounded agent decisions inside well-defined nodes rather than giving the model unrestricted control over the entire system.

## Q19. How would you design a supervisor-agent architecture?

Answer:

I would use a supervisor that selects from a fixed set of allowed specialist tasks.

For example:

* Research specialist: gathers and summarizes evidence.

* Portfolio-risk specialist: evaluates defined risk dimensions.

* Evidence specialist: checks source quality and claim support.

* Report synthesizer: combines validated results.

The supervisor would not generate arbitrary executable instructions. It would return a typed routing decision, validated against an allowlist.

I would enforce a maximum number of transitions, timeouts, retry budgets, and a terminal failure state. The final aggregation step would check that required specialist outputs exist and are mutually consistent.

## Q20. How would you implement conditional routing?

Answer:

I would represent the routing decision as a constrained enum or typed object, for example:

Python

Run

```
from enum import StrEnum

class NextStep(StrEnum):
    RESEARCH = "research"
    RISK = "risk"
    EVIDENCE_REVIEW = "evidence_review"
    HUMAN_REVIEW = "human_review"
    FINISH = "finish"
```

The supervisor's output would be validated, and the graph would map each permitted value to a known node.

I would never take an arbitrary model-generated string and use it as a function name, import path, or executable tool target.

## Q21. What are reducers in LangGraph?

Answer:

Reducers define how state updates from graph nodes are combined.

For example, if parallel agents return evidence items, a reducer can merge them into a shared evidence collection.

The reducer must have clear semantics. If two agents update the same field, I need to decide whether to append, overwrite, deduplicate, or reject conflicting values.

For financial research, I would preserve provenance and avoid silently overwriting contradictory evidence.

## Q22. How would you prevent infinite agent loops?

Answer:

I would apply several controls:

1. A maximum graph step count.

2. A maximum number of tool calls.

3. Per-node and overall timeouts.

4. A retry budget with exponential backoff and jitter.

5. A repeated-state or repeated-action detector where appropriate.

6. Explicit terminal states for failure and escalation.

The model should not be able to increase these limits by generating a tool call or modifying its own instructions.

## Q23. How would you implement durable checkpointing?

Answer:

I would configure a persistent LangGraph checkpointer backed by a production-supported database integration. Each workflow execution would have a stable thread or execution identifier.

I would persist enough state to resume safely, including the workflow stage, validated outputs, and pending human decision.

I would also define retention, encryption, tenant isolation, and recovery behavior. Checkpointing alone is not enough: external side effects must be idempotent, because a resumed workflow may re-enter a node.

## Q24. How would you implement Human-in-the-Loop (HITL)?

Answer:

I would use a durable workflow interruption before the report reaches its final approved state.

The process would be:

1. The workflow generates a draft report.

2. It validates required evidence and risk fields.

3. It reaches a human-review node.

4. The graph pauses and persists its checkpoint.

5. An authorized reviewer approves, rejects, or requests changes.

6. The API validates the reviewer, tenant, and decision.

7. The workflow resumes from the checkpoint with the decision.

8. The final state and audit event are persisted.

In the current project, the application layer has reviewer authorization and review-state handling, but that is not the same as a durable graph-level interrupt and resume. I would implement the latter for a production workflow.

## Q25. What happens if a human reviewer never responds?

Answer:

I would keep the review in a pending state and apply a defined SLA.

The system could send reminders, escalate to another authorized reviewer, or expire the review according to business policy.

I would not automatically approve a report just because the review timed out. The workflow should remain paused or transition to an explicit expired/escalated state.

# 4. RAG, embeddings, and retrieval

## Q26. Why does your project need RAG?

Answer:

Financial research needs to be grounded in specific sources rather than relying entirely on a model's pretrained knowledge.

RAG allows the system to retrieve relevant evidence and pass it into the analysis step. This can improve factual grounding and make it possible to trace report claims back to source material.

However, RAG does not guarantee correctness. Retrieval can miss relevant information, sources can be stale, and the model can misinterpret evidence. Those risks require evaluation and validation.

## Q27. Explain the complete production RAG pipeline you would build.

Answer:

I would separate ingestion from query-time retrieval.

Ingestion:

1. Acquire documents from approved sources.

2. Validate source identity and permissions.

3. Extract text and metadata.

4. Normalize and deduplicate.

5. Chunk the content.

6. Generate embeddings.

7. Store text, metadata, and vectors.

8. Record source versions and ingestion status.

Query time:

1. Authenticate the user and resolve tenant scope.

2. Normalize the research query.

3. Apply metadata and access filters.

4. Retrieve candidates through vector and keyword search.

5. Merge and rerank candidates.

6. Apply freshness and source-quality rules.

7. Pass bounded evidence to the analysis model.

8. Validate citations and claims.

9. Store the report with evidence provenance.

The current project has a pgvector schema and evidence-retrieval abstractions, but that alone does not establish that the complete ingestion and embedding pipeline is implemented end to end.

## Q28. Why PostgreSQL with pgvector instead of a dedicated vector database?

Answer:

PostgreSQL with pgvector is attractive when the application already needs relational data, transactions, tenant metadata, and vector similarity search.

It can simplify operations because the team manages fewer data systems. It also allows relational filters and vector retrieval to coexist.

A dedicated vector database may be appropriate when vector-specific scale, indexing, throughput, or operational features justify a separate system.

I would benchmark realistic workloads before deciding. The right choice depends on corpus size, update frequency, filtering patterns, latency targets, and operational constraints.

## Q29. Why do you have a 384-dimensional vector column?

Answer:

The database column is configured for 384-dimensional embeddings. That means the embedding model used to populate it must produce vectors of exactly that dimension.

I would make the embedding model and dimension part of versioned configuration and validate dimensions before insertion.

If we change to a model with a different dimension, I would not simply write new vectors into the existing column. I would plan a migration, re-embedding strategy, and compatibility window.

## Q30. What is the difference between vector search and keyword search?

Answer:

Keyword search matches lexical terms. It works well for exact names, identifiers, ticker symbols, and phrases.

Vector search compares semantic representations. It can retrieve conceptually related passages even when the wording differs.

For financial research, I would usually combine them. A ticker such as `AAPL`, a specific filing identifier, or a regulation number may require lexical matching, while a query about “increasing liquidity pressure” may benefit from semantic retrieval.

## Q31. What is hybrid search?

Answer:

Hybrid search combines lexical and semantic retrieval.

One approach is to retrieve candidates from both BM25 and vector search, then merge their rankings using Reciprocal Rank Fusion (RRF). The merged candidates can then be reranked.

I would evaluate hybrid retrieval against each individual method using a labeled query set rather than assuming it is always better.

## Q32. How would you choose a chunking strategy?

Answer:

I would choose chunking based on document structure and the type of question.

For financial documents, I would preserve meaningful boundaries such as sections, tables, disclosures, and paragraphs. Arbitrary fixed-size chunks can split important context or separate a claim from its qualifications.

I would store metadata such as document ID, source, page or section, publication time, version, and access scope.

I would evaluate chunk size and overlap empirically using retrieval recall, precision, and downstream answer quality.

## Q33. What is reranking, and why use it?

Answer:

Initial retrieval prioritizes recall: it finds a candidate set likely to contain relevant evidence.

A reranker evaluates query-document relevance more precisely and reorders those candidates. I would retrieve a manageable candidate set, rerank it, and send only the most useful evidence to the LLM.

The trade-off is additional latency and compute. I would use reranking where measured improvements in evidence quality justify the cost.

## Q34. How would you handle stale financial information?

Answer:

I would store publication time, ingestion time, source version, and—where relevant—the period to which the information applies.

Retrieval would use freshness rules appropriate to the question. Market prices require different freshness constraints from an annual report.

I would also distinguish the document's publication date from the date of the underlying data. The report should make those timestamps visible, and stale or missing data should trigger a warning or block the analysis when freshness is essential.

## Q35. How would you evaluate RAG quality?

Answer:

I would evaluate multiple layers:

* Retrieval: precision@k, recall@k, MRR, nDCG.

* Grounding: whether claims are supported by retrieved evidence.

* Answer quality: correctness, completeness, and relevance.

* Citation quality: whether cited sources actually support the claims.

* Operational performance: latency, failure rate, and cost.

I would create a representative, human-reviewed evaluation set. Automated metrics can help with regression testing, but high-impact financial outputs also need expert review.

## Q36. What would you do if retrieval returns no useful evidence?

Answer:

The system should not invent an answer.

I would allow a bounded reformulation or alternative retrieval attempt if the policy permits it. If evidence remains insufficient, the report should explicitly state that the available evidence is insufficient and either ask for clarification or route the request to a human analyst.

The workflow should distinguish “no evidence found” from “evidence found that supports a negative conclusion.”

# 5. LLMs, structured output, and hallucinations

## Q37. Why use structured output instead of free-form text?

Answer:

Structured output gives downstream services a predictable contract.

A report might contain a summary, findings, evidence references, risk categories, confidence indicators, and review requirements. I would validate that output against a Pydantic schema before persisting or passing it to another component.

Schema validity does not guarantee factual correctness, so I would also validate citations, required evidence, and business rules.

## Q38. How do you reduce hallucinations?

Answer:

I would use several complementary controls:

1. Ground the model in retrieved evidence.

2. Require claim-level citations for factual statements.

3. Validate source IDs against retrieved evidence.

4. Separate facts from inference and uncertainty.

5. Use deterministic rules for critical constraints.

6. Evaluate outputs against a human-reviewed dataset.

7. Escalate unsupported high-impact claims.

I would not claim that prompt engineering or a low temperature eliminates hallucinations.

## Q39. What temperature would you use?

Answer:

For repeatable financial research outputs, I would generally start with a low temperature.

But temperature is not a correctness control. I would focus more on grounding, schema validation, deterministic business rules, and evaluation.

I would tune generation settings against a task-specific evaluation set.

## Q40. How would you handle malformed JSON from the model?

Answer:

I would validate the output using a strict schema.

If validation fails, I would allow a limited repair attempt that includes the validation errors, while keeping the original output for diagnostics. If the output still fails, I would mark the workflow as failed or send it for review.

I would not silently coerce arbitrary output into a valid report if doing so could change its meaning.

## Q41. How would you manage LLM provider failures?

Answer:

I would use explicit timeouts, bounded retries, exponential backoff with jitter, and provider-specific rate-limit handling.

I would classify errors into transient failures, permanent request errors, authentication/configuration errors, and quota exhaustion.

A fallback provider can improve availability, but I would only use it if its model is approved for the data classification and has passed the relevant quality and security evaluations.

## Q42. How would you control LLM cost?

Answer:

I would track token usage and cost per request, tenant, workflow, model, and task.

I would reduce unnecessary context, cache only safe and reusable results, use smaller models for suitable subtasks, and enforce budgets.

For high-value tasks, I would optimize for total cost per correct, reviewable result—not merely the lowest token cost.

# 6. Financial data, tools, and risk analysis

## Q43. How would you integrate market data?

Answer:

I would define a provider interface and implement adapters for approved, licensed data vendors.

The normalized result would include the instrument, value, currency, observation timestamp, provider, methodology, and any delay indicator.

The application would validate freshness and provenance before using the data. If a required provider is unavailable, the system should fail closed or clearly mark the analysis as incomplete rather than inventing market values.

The current project includes a market-data abstraction, but the default adapter does not provide a complete live, licensed data feed.

## Q44. Why should financial calculations not be left entirely to an LLM?

Answer:

LLMs are useful for interpreting information and explaining results, but they are not a substitute for deterministic financial computation.

For calculations such as returns, exposure, volatility, or portfolio weights, I would use tested numerical code with explicit input validation, units, and rounding rules.

The LLM can explain the results, while the calculation engine remains the source of truth.

## Q45. How would you calculate portfolio risk?

Answer:

First, I would clarify which risk measure is required and the assumptions behind it.

For example, historical volatility requires a defined return series and sampling frequency. Value at Risk requires a confidence level and methodology. Portfolio risk also depends on weights, correlations, and the period being analyzed.

I would implement calculations in a deterministic numerical module, test them against known examples, and document assumptions. I would not present a risk metric without its methodology and data timestamp.

## Q46. How would you handle conflicting sources?

Answer:

I would preserve both sources and their provenance rather than silently choosing one.

The system would compare publication time, authority, methodology, and the data period. It could flag a conflict and ask the analyst to resolve it.

A source-ranking policy can prioritize certain sources, but the policy should be explicit, versioned, and auditable.

## Q47. How would you prevent a tool from returning unauthorized data?

Answer:

Tool authorization must be enforced by the application, not entrusted to the LLM.

Every tool invocation should receive a trusted tenant and user context. The tool should validate authorization, restrict the query scope, and return only permitted data.

I would also validate tool arguments, impose result limits, audit access, and test cross-tenant access attempts.

# 7. FastAPI, PostgreSQL, Redis, and Celery

## Q48. Explain the API request flow.

Answer:

A request enters through a FastAPI route. The API validates the request schema and authenticates the caller. It then invokes the application use case through injected dependencies.

The use case checks business constraints and interacts with repositories and the workflow. The result is persisted and returned through a response schema.

For long-running research, I would change the current inline execution to asynchronous job submission.

## Q49. Why should long-running AI work not run inside the API request?

Answer:

Long-running model calls and retrieval workflows consume request capacity and make client timeouts more likely.

I would make the API accept the request, persist a job, and enqueue background work. The client receives a job or review ID and can poll for status or receive a notification.

The current implementation runs the review workflow inline, so Celery integration is a production improvement rather than a capability I would claim is already complete.

## Q50. How would you design the Celery workflow?

Answer:

I would separate request acceptance from execution.

1. Validate and persist the request.

2. Persist an outbox event in the same database transaction.

3. A dispatcher publishes the event to the queue.

4. A Celery worker loads the request and runs the workflow.

5. The worker persists progress and final status.

6. The API exposes status and result endpoints.

The outbox prevents a database commit from succeeding while queue publication is lost. I would also use idempotent task handling because Celery tasks may execute more than once.

## Q51. Why Redis?

Answer:

Redis can support queue brokering, caching, rate-limit counters, and other low-latency coordination tasks.

I would not use Redis as the only durable source of truth for review records or audit history. PostgreSQL would remain the authoritative store for business state.

I would also define Redis eviction, persistence, access controls, and failure behavior according to its role.

## Q52. What is idempotency, and how does your project handle it?

Answer:

Idempotency means repeated submissions of the same logical request do not create unintended duplicate effects.

The project has a request fingerprint based on a canonicalized payload and tenant. That is useful for identifying equivalent requests, but computing a fingerprint alone does not guarantee idempotency.

To enforce it, I would persist the idempotency key or fingerprint with a unique constraint, define key-retention rules, and return the original request result for a duplicate submission.

## Q53. How would you handle duplicate Celery tasks?

Answer:

I would make task execution safe to repeat.

The worker would check the job's state, use a stable job identifier, and enforce valid state transitions. Database uniqueness constraints would protect against duplicate records.

For external side effects, I would use idempotency keys where supported. I would not assume that a Celery acknowledgement setting alone prevents duplicates.

## Q54. How would you design database transactions?

Answer:

I would keep transactions short and avoid holding database locks while waiting for LLM or external network calls.

For asynchronous processing, I would persist the request and job state in a transaction, commit, and then perform the expensive work outside that transaction.

State changes such as approval should use a transaction with concurrency-safe checks, so two reviewers cannot independently make conflicting decisions.

## Q55. How would you prevent two reviewers from deciding the same review simultaneously?

Answer:

I would enforce the state transition atomically.

For example, an update could succeed only when the current status is `AWAITING_REVIEW`. The application would check the affected row count and reject a second decision if the state has already changed.

For more complex transitions, I could use optimistic versioning or a row-level lock. The database constraint and transaction—not just an in-memory check—must protect the invariant.

# 8. Security, multi-tenancy, and governance

## Q56. How would you implement multi-tenant isolation?

Answer:

Every tenant-owned record would have a tenant identifier. The authenticated identity would establish the tenant context; the request body would not be trusted to choose an arbitrary tenant.

Repositories would scope reads and writes by tenant. I would also consider PostgreSQL Row-Level Security as defense in depth.

I would test direct-object-reference attacks, background-job tenant context, vector retrieval filters, and cache-key isolation.

## Q57. How would you implement RBAC?

Answer:

I would define permissions based on roles and actions.

For example, analysts may create and view permitted reports, reviewers may decide reviews assigned to them, and administrators may manage configuration.

I would validate permissions at the application use-case boundary and enforce object-level and tenant-level authorization. A role check alone is insufficient if the user can access another tenant's review.

## Q58. How would you secure JWT authentication?

Answer:

I would validate the token signature, allowed algorithm, issuer, audience, expiry, and relevant claims.

Signing keys would be stored securely and rotated. Access tokens would have limited lifetimes, and refresh-token handling would follow a defined revocation policy.

I would never trust a role or tenant claim without validating the token and the claim's intended semantics.

## Q59. How do you protect against prompt injection?

Answer:

Retrieved documents are untrusted input, even if they come from an approved source.

I would treat document content as data, not instructions. The system prompt would clearly separate trusted instructions from retrieved context, and tools would have explicit allowlists and authorization checks.

I would also test indirect prompt injection, malicious links, tool-argument manipulation, and attempts to extract system instructions or other tenants' data.

Prompt wording alone is not a sufficient defense.

## Q60. How would you protect sensitive financial data?

Answer:

I would classify data and minimize what is sent to external providers.

Controls would include encryption in transit and at rest, secret management, least-privilege access, tenant isolation, audit logging, retention policies, and redaction of sensitive data from logs.

For LLM providers, I would verify contractual data-handling terms, retention settings, regional requirements, and whether the provider is approved for the data category.

## Q61. What should be included in the audit trail?

Answer:

I would record who initiated the review, which data sources and versions were used, which model and prompt version generated the report, the workflow version, validation results, and human decisions.

Audit records should be append-only from the application's perspective, access-controlled, and protected against tampering.

I would avoid logging secrets or unnecessary sensitive document content. A report should be reproducible to the extent that the source data, model version, and external dependencies permit it.

## Q62. How would you handle an unsafe or unsupported financial claim?

Answer:

I would use a validation layer that checks whether required claims have supporting evidence and whether the report violates defined business policies.

Unsupported claims should be removed, qualified, or flagged for human review according to policy. The model should not be permitted to convert missing evidence into certainty.

The final report should make uncertainty and limitations visible.

# 9. Testing and evaluation

## Q63. What testing strategy would you use?

Answer:

I would use a testing pyramid:

* Unit tests for domain rules, validation, routing, and calculations.

* Adapter tests for database, LLM, and provider integrations.

* API tests for authentication, schemas, and authorization.

* Workflow tests for state transitions, retries, and failure paths.

* End-to-end tests for the complete research journey.

* AI evaluation tests for retrieval, grounding, citations, and report quality.

I would keep most tests deterministic by using fixtures and fake adapters. Live-provider tests would run selectively because they can be costly and nondeterministic.

## Q64. How would you test LangGraph?

Answer:

I would test individual nodes and complete graph paths.

Cases would include successful retrieval, empty evidence, model timeout, malformed structured output, retry exhaustion, human interruption, resume, rejection, and duplicate execution.

I would also test that the graph cannot exceed its step budget and that invalid routing decisions fail safely.

## Q65. How would you test an LLM application when outputs are nondeterministic?

Answer:

I would combine deterministic contract tests with statistical or rubric-based evaluation.

Contract tests verify schema validity, citation structure, and business invariants. An evaluation dataset measures answer correctness, grounding, and relevance.

For quality comparisons, I would track model and prompt versions and compare performance over a representative dataset. I would use human review for high-impact errors and investigate regressions rather than relying on a single aggregate score.

## Q66. What is the difference between RAGAS and ordinary unit testing?

Answer:

Unit tests verify explicit software behavior, such as whether a repository filters by tenant or a state transition rejects an invalid decision.

RAGAS-style evaluation estimates aspects of RAG quality, such as faithfulness, answer relevance, and context precision or recall.

These are complementary. Evaluation metrics can be imperfect proxies, so I would combine them with labeled test cases, citation checks, and expert review.

## Q67. How would you test for cross-tenant data leakage?

Answer:

I would create test tenants with deliberately distinguishable documents and records.

Then I would test:

* Direct record access using another tenant's ID.

* Search and vector retrieval filters.

* Cache-key collisions.

* Background jobs with missing or altered tenant context.

* Reviewer access to another tenant's work.

* Administrative exceptions and audit events.

I would include negative authorization tests in CI, not only manual security testing.

# 10. Scalability, performance, and reliability

## Q68. How would you scale this system to millions of requests?

Answer:

First, I would clarify whether that means millions per day, per hour, or per second, and whether requests are short API calls or long-running research jobs.

For a high-volume deployment, I would:

* Scale stateless API instances horizontally.

* Separate API traffic from worker execution.

* Scale workers based on queue depth and processing latency.

* Use database connection pooling and tune query patterns.

* Optimize vector indexes and tenant filters.

* Cache only safe, reusable results.

* Apply per-tenant quotas and admission control.

* Isolate expensive workflows from latency-sensitive endpoints.

I would not promise a particular throughput without workload modeling and load testing.

## Q69. How would you identify bottlenecks?

Answer:

I would instrument the request path with distributed tracing and measure latency for each stage: API handling, database access, retrieval, reranking, model calls, and serialization.

I would inspect p50, p95, and p99 latency, error rate, queue age, connection-pool saturation, token usage, and cost.

Then I would optimize the measured bottleneck. Adding more application instances does not solve every database, external-provider, or model-capacity bottleneck.

## Q70. What caching strategy would you use?

Answer:

I would distinguish between caching source data, retrieval results, embeddings, and generated answers.

Every cache key should include relevant tenant, authorization, query, model, prompt, and source-version context. Otherwise, a cache can return stale or unauthorized data.

For financial information, freshness is essential. Market data may need a short time-to-live or no cache at all, depending on the data contract and use case.

## Q71. How would you handle backpressure?

Answer:

I would bound the queue, limit concurrent work per tenant, and reject or defer requests when capacity is exhausted.

The API should return a clear status such as accepted, throttled, or temporarily unavailable. Workers should not continue accepting unlimited work when downstream model providers or databases are saturated.

Backpressure protects the system from turning a temporary slowdown into a cascading failure.

## Q72. How would you design retries?

Answer:

Retries should be limited to transient failures and should respect idempotency.

I would use exponential backoff with jitter, a maximum attempt count, and an overall deadline. Invalid inputs and authorization failures should not be retried.

After retries are exhausted, the job should enter a terminal failure state or a dead-letter workflow with enough context for investigation.

## Q73. How would you make the service highly available?

Answer:

I would deploy stateless API replicas across failure domains, use managed and appropriately configured database infrastructure, and make background processing recoverable.

I would define recovery objectives, backups, restore tests, health checks, and dependency failure behavior.

High availability is an end-to-end property. Multiple API replicas do not help if the database, queue, or external model provider is a single point of failure.

# 11. Observability, deployment, and operations

## Q74. What would you monitor in production?

Answer:

I would monitor four groups of signals.

| Area       | Metrics                                              |
| ---------- | ---------------------------------------------------- |
| API        | Request rate, errors, latency, saturation            |
| Workflow   | Queue age, execution duration, retries, stuck jobs   |
| AI quality | Grounding, citation validity, evaluation regressions |
| Cost       | Tokens, model spend, cost per report, cache hit rate |

I would also propagate a correlation ID across the API, worker, graph, and external calls.

## Q75. Why use OpenTelemetry?

Answer:

OpenTelemetry provides a standard way to emit traces, metrics, and logs.

For this application, I would trace the full research request across FastAPI, Celery, PostgreSQL, retrieval, and model-provider calls.

I would be careful not to place sensitive prompts, documents, access tokens, or personally identifiable information into telemetry by default.

## Q76. How would you deploy the platform?

Answer:

I would containerize the API and worker separately and deploy them with explicit configuration, health checks, resource limits, and secret management.

I would run database migrations as a controlled deployment step, not independently from every API replica.

For Kubernetes, I would use separate workloads for API and workers, configure autoscaling against meaningful metrics, and define rollout and rollback procedures.

I would also test restore and rollback paths, not just the happy-path deployment.

## Q77. How would you manage database migrations?

Answer:

I would use Alembic migrations with a clear upgrade path.

For changes that affect a live system, I would prefer expand-and-contract migrations: add compatible schema first, deploy code that supports both versions if needed, backfill data, and remove old schema only after the transition.

Vector dimension changes and embedding-model changes require a deliberate migration plan, not merely an ORM model update.

## Q78. How would you handle a production incident where report generation suddenly fails?

Answer:

I would first establish the blast radius and whether the failure is isolated to one provider, tenant, or workflow stage.

I would inspect traces, error rates, queue depth, recent deployments, provider status, and database health. If necessary, I would disable the failing integration or pause new work while preserving existing jobs.

After mitigation, I would identify the root cause, recover affected jobs safely, and add a regression test and operational alert.

# 12. Difficult Staff-level system design questions

These questions test whether you can make decisions under constraints rather than simply describe a framework.

## Q79. Design this platform for 10,000 concurrent users.

Answer:

I would begin by clarifying workload shape: request rate, report duration, data size, tenant distribution, and latency requirements.

I would separate the synchronous control plane from asynchronous research execution. The API would authenticate and persist requests quickly; workers would perform retrieval and model calls.

I would use bounded concurrency, per-tenant quotas, connection pooling, queue-based backpressure, and independently scalable workers. I would load-test the database and vector retrieval path because they may become bottlenecks before the API layer.

I would not treat 10,000 connected users as equivalent to 10,000 simultaneous LLM calls.

## Q80. What if the LLM is unavailable for 30 minutes?

Answer:

The platform should continue to accept or defer requests only within defined capacity and product requirements.

Jobs would remain pending or retryable, with bounded retry schedules. The system should expose the degraded state and avoid consuming unlimited resources.

If an approved fallback model exists, I would route eligible work to it. Otherwise, I would preserve the request and resume processing when service returns. I would not silently produce a lower-quality result without recording the model change.

## Q81. What if PostgreSQL is unavailable after the model has generated a report?

Answer:

The system should not claim the report is complete if it has not been durably persisted.

I would retry the persistence operation within a bounded window. If that fails, the worker should retain enough execution context to recover safely, ideally through durable workflow state and job records.

This is one reason I would avoid holding a database transaction open during model generation. I would also consider how to recover a generated result without paying for the model call again.

## Q82. How would you guarantee exactly-once processing?

Answer:

I would avoid promising true end-to-end exactly-once execution across a database, message broker, and external LLM provider.

In practice, I would design for at-least-once delivery with idempotent processing, unique constraints, transactional state transitions, and deduplicated side effects.

The business outcome can be effectively once-only even when the underlying task may execute more than once.

## Q83. Would you use Kafka instead of Celery and Redis?

Answer:

I would choose based on requirements.

Celery with Redis is suitable for background task execution with retries and task-oriented processing. Kafka is designed for durable event streams, replay, and multiple independent consumers.

If the main requirement is executing research jobs, Celery may be sufficient. If the platform needs an event backbone with replayable domain events and multiple consumer groups, Kafka may be justified.

I would not add Kafka just because the system is described as enterprise-grade.

## Q84. Would you use PostgreSQL or a separate vector database at very large scale?

Answer:

I would benchmark both using representative data, query filters, update rates, and concurrency.

PostgreSQL offers relational consistency and operational simplicity. A dedicated vector database may offer different scaling and indexing characteristics.

I would also consider the complexity of keeping relational metadata and vectors synchronized if they live in separate systems. The decision should follow measured requirements, not a general assumption that one database is always better.

## Q85. How would you version prompts, models, and workflows?

Answer:

I would version them independently and record their identifiers with each report.

A report should capture the model, prompt template, workflow version, embedding model, retrieval configuration, and relevant source versions.

This supports reproducibility, incident investigation, and controlled evaluation. A new prompt or model should pass evaluation gates before it becomes the default.

## Q86. How would you roll out a new model safely?

Answer:

I would first evaluate it offline on a representative dataset.

Then I would run shadow traffic or a limited canary where feasible, compare quality, latency, failure rates, and cost, and inspect high-impact regressions.

I would use a feature flag or versioned routing configuration to control rollout and provide a rollback path. I would not switch every tenant to a new model solely because it performs better on one aggregate metric.

## Q87. How would you make reports explainable?

Answer:

I would make the report's evidence trail explicit.

Each material claim should reference the source passages supporting it. The report should distinguish source facts, derived calculations, and model-generated interpretations.

I would also retain the source version, timestamps, calculation methodology, and model/workflow versions. This provides practical traceability without pretending that an LLM's internal reasoning is a reliable audit record.

## Q88. How would you decide what to build first?

Answer:

I would prioritize the minimum end-to-end workflow that produces a useful and verifiable result.

My initial priorities would be:

1. Reliable source ingestion and provenance.

2. Tenant-safe retrieval.

3. Grounded structured report generation.

4. Durable persistence and valid state transitions.

5. Human review and auditability.

6. Evaluation and operational visibility.

7. Background processing and scaling.

I would avoid building a complex multi-agent framework before proving that retrieval quality, report usefulness, and the review workflow meet the business requirements.

# 13. Questions about gaps in your current implementation

These are especially likely if the interviewer reviews your repository.

## Q89. Your LLM adapter is a mock. Why?

Answer:

“The mock adapter allows me to develop and test the workflow without relying on an external provider. It makes tests deterministic and isolates orchestration logic from model behavior.

It is not a production LLM integration. The next step is to implement a provider-backed adapter behind the same interface, including timeouts, retries, structured-output validation, telemetry, and secure configuration.

I would evaluate the real adapter before describing the platform as production-ready.”

## Q90. Your workflow executes inline. Why is Celery present?

Answer:

“Celery is an integration point for asynchronous processing, and the repository includes a worker task scaffold. However, the review creation use case currently invokes the workflow inline.

I would connect the two by persisting the review and an outbox event, dispatching the event to Celery, and returning a job identifier. The worker would execute the graph and update the persisted status.”

## Q91. Your handoff logic exists, but the graph does not use separate specialist nodes. Is that really multi-agent?

Answer:

“Not yet. The handoff logic expresses potential routing decisions, but the graph currently follows a sequential two-node path.

I would implement specialist nodes and explicit conditional edges, define typed contracts for each specialist, and add bounded supervisor routing. Until that is complete, I would call this an agentic workflow foundation rather than a full multi-agent implementation.”

## Q92. You have pgvector in the schema. Does that mean you have a complete RAG pipeline?

Answer:

“No. A vector column is one component of a RAG system.

A complete pipeline also requires ingestion, chunking, embedding generation, vector persistence, metadata filtering, retrieval, ranking, and evaluation.

I would verify each stage end to end and test that the embedding dimension, model version, tenant filter, and source provenance remain consistent.”

## Q93. The project has a request fingerprint. Does that guarantee idempotency?

Answer:

“No. A fingerprint helps identify equivalent requests, but it does not prevent duplicates by itself.

I would persist the fingerprint or idempotency key with a unique constraint, define how duplicate requests are handled, and make the worker safe to execute more than once.”

## Q94. Is the current HITL implementation durable?

Answer:

“The application layer supports reviewer authorization and review-state decisions. However, a durable graph interruption and resume mechanism requires a persistent checkpoint and an explicit pause/resume flow.

I would add that using LangGraph's checkpointing and interrupt/resume facilities, then test process restarts, duplicate decisions, and concurrent reviewer actions.”

## Q95. Would you call this production-ready?

Answer:

“I would call it an architectural foundation or prototype with several production-oriented boundaries, not a fully production-ready financial platform.

Before production, I would complete the real LLM and market-data integrations, end-to-end RAG ingestion and retrieval, asynchronous workflow execution, durable HITL, stronger idempotency, tenant isolation tests, observability, and AI evaluation.

I would then validate the system against defined security, reliability, latency, and quality requirements.”

That answer demonstrates engineering judgment. It is better than defending incomplete functionality as complete.

# 14. Rapid-fire questions

Use these for short-answer interview practice.

| Question                                   | Senior-level answer                                                                      |
| ------------------------------------------ | ---------------------------------------------------------------------------------------- |
| Why FastAPI?                               | Typed APIs, dependency injection, async support, and OpenAPI integration.                |
| Why PostgreSQL?                            | Relational consistency, transactions, mature tooling, and structured metadata.           |
| Why pgvector?                              | Vector similarity search alongside relational data and filters.                          |
| Why LangGraph?                             | Explicit stateful workflows, routing, and checkpoint support.                            |
| Why Celery?                                | Background task execution, retries, and worker scaling.                                  |
| Why Redis?                                 | Low-latency caching and queue-related use cases.                                         |
| Why Pydantic?                              | Runtime validation and typed API/data contracts.                                         |
| Why SQLAlchemy?                            | ORM and database access abstraction.                                                     |
| Why Alembic?                               | Versioned, repeatable database schema migrations.                                        |
| Why OpenTelemetry?                         | Standardized traces, metrics, and instrumentation.                                       |
| Why not only an LLM?                       | Deterministic rules and validated data are needed for correctness.                       |
| Why not fine-tune immediately?             | First establish retrieval quality, evaluation, and a clear reason fine-tuning is needed. |
| Why not use agents for everything?         | Agents add cost and uncertainty; deterministic workflows are easier to control.          |
| Why use human review?                      | High-impact outputs may require authorized human judgment.                               |
| What is the main RAG risk?                 | Missing or misleading evidence can lead to unsupported conclusions.                      |
| What is the main multi-tenant risk?        | Cross-tenant data leakage through queries, caches, tools, or authorization bugs.         |
| What is the main distributed-systems risk? | Partial failure, duplicate execution, and inconsistent state.                            |
| What is the main AI operations risk?       | Quality drift, provider failures, latency, and unpredictable cost.                       |

# 15. A complete system-design answer you can deliver

If the interviewer asks, “Design an enterprise financial research copilot from scratch,” you can use this answer structure.

## Your 5-minute answer framework

1. Clarify requirements

   Establish user types, data sources, request volume, latency, freshness, tenant model, review requirements, and whether the system may provide recommendations or only research support.

2. Define the core architecture

   Start with a modular application: FastAPI, application use cases, domain models, repository ports, and infrastructure adapters.

3. Design the RAG pipeline

   Ingest approved sources, preserve provenance, chunk and embed documents, perform hybrid retrieval, rerank, and produce evidence-grounded output.

4. Design the workflow

   Use explicit graph nodes for retrieval, analysis, validation, and human review. Add specialist agents only where they provide a measurable benefit.

5. Make execution durable

   Persist requests, enqueue background jobs through an outbox, use idempotent workers, and support durable checkpoint/resume.

6. Secure the platform

   Enforce tenant-scoped authorization, RBAC, secrets management, data minimization, and auditable human decisions.

7. Operate and scale

   Instrument traces and metrics, evaluate AI quality, enforce cost budgets, and scale API and worker capacity independently.

A good Staff-level conclusion is:

> “I would optimize for trustworthy, reviewable research rather than maximum autonomy. The model is one component of the system; data quality, evidence provenance, deterministic validation, authorization, durable state, and operational controls are equally important. I would start with a small, testable workflow and introduce additional agents or infrastructure only when the requirements and measured bottlenecks justify them.”

# 16. How to prepare for the interview

### Preparation checklist

0/15 completed

1. Project architecture

Explain the end-to-end request flow

Explain ports, adapters, repositories, and DI

Explain why this is not yet a microservices system

2. AI and RAG

Explain ingestion and retrieval end to end

Explain hybrid search, reranking, and freshness

Explain grounding, citation validation, and evaluation

3. Agents and HITL

Explain current graph nodes accurately

Explain supervisor routing and bounded agents

Explain durable interrupt, checkpoint, and resume

4. Production engineering

Explain Celery, outbox, retries, and idempotency

Explain tenant isolation and concurrent review decisions

Explain observability, scaling, and failure recovery

5. Project honesty

Explain the mock LLM adapter

Explain inline workflow and worker scaffold

Explain the gap between pgvector schema and complete RAG

Reset checklist

My recommendation for your preparation: master the current implementation first, especially the distinction between implemented features and planned production improvements. Then practice the system-design questions aloud. At Senior/Staff level, interviewers often probe the same architecture from different angles—failure handling, data consistency, security, cost, and trade-offs—so being able to defend the reasoning matters more than memorizing a long list of definitions.
