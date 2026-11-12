# Financial Compliance AI Platform — Interview Question Bank

Below is a comprehensive interview preparation guide for your project, covering Senior AI Engineer, Staff AI Engineer, and AI Architect discussions.

I've organized the questions by topic so you can prepare progressively. The answers are written in the first person, as if you are explaining your own engineering decisions to an interviewer.

The questions cover the actual project areas, including its agents, retrieval strategies, LangGraph workflow, database, Celery workers, security, HITL, testing, and production-readiness considerations. Your ZIP also contains dedicated architecture, data-model, operations, agent-contract, and production-readiness documents, along with tests for planner behavior, guardrails, RBAC, and state transitions.

How to use this guide: Learn the short answer first. Then practice explaining the trade-offs, failure scenarios, and limitations. At staff level, the interviewer is evaluating your engineering judgment as much as your knowledge of the frameworks.

# Part 1 — Project overview and architecture

## Q1. Explain your project end to end.

Answer:

"I built an AI-powered financial compliance review platform that helps compliance teams evaluate financial communications against an approved policy knowledge base.

The user submits a statement through FastAPI. The API authenticates the user, validates their permissions, creates a review record, and queues a background job through Celery.

The worker retrieves relevant policies from PostgreSQL using pgvector semantic search, with keyword retrieval as a fallback. A LangGraph workflow then coordinates a planner, supervisor, and specialist agents covering performance, risk, fees, and general policy requirements.

The outputs are consolidated and validated through deterministic guardrails. The workflow then pauses for an authorized human reviewer. Once the reviewer approves or rejects the assessment, the workflow resumes and records the decision.

The primary design principle is that the LLM performs analysis, while deterministic application code controls access, execution, evidence validation, and the approval boundary."

## Q2. What business problem does it solve?

Answer:

"Financial compliance teams must compare marketing statements, advisor communications, and product descriptions against large sets of policies. This involves locating relevant clauses, checking claims, documenting evidence, and routing findings for review.

My platform automates parts of that process by retrieving relevant policy evidence and generating structured, traceable findings.

It is a decision-support system rather than an autonomous legal authority. The intended benefits are reduced manual research effort, consistent review structure, and better traceability. I would validate those benefits through reviewer time measurements, evidence quality, and override rates."

## Q3. What is the overall architecture?

Answer:

"I use a layered application architecture combined with an asynchronous processing architecture and a stateful AI workflow.

The API layer handles HTTP and security. The service and repository layers manage business operations and persistence. Celery separates long-running processing from the API. PostgreSQL stores the system of record and supports vector retrieval through pgvector. LangGraph coordinates the analysis and human approval lifecycle.

I chose these boundaries because the API, database, AI workflow, and human review process have different responsibilities and scaling characteristics."

## Q4. Why did you choose this architecture?

Answer:

"The workflow has long-running model calls, multiple independent analysis tasks, conditional branches, and a human approval stage that can last hours or days.

A synchronous API with a single LLM call would not handle those requirements cleanly. I separated request handling from execution, made workflow state explicit, and persisted the state required for recovery.

This gives us independent worker scaling, testable business boundaries, and a controlled human decision process without introducing a separate microservice for every component."

## Q5. Why not build everything as microservices?

Answer:

"Microservices would provide independent deployment and scaling, but they would also introduce network boundaries, distributed transactions, service discovery, more deployment pipelines, and additional failure modes.

The project has clear logical modules, but logical modularity does not require every module to be a network service.

I would initially deploy the API and worker separately while keeping the domain, retrieval, and orchestration modules modular. I would extract a service only when independent scaling, ownership, security isolation, or deployment cadence justified the additional complexity."

## Q6. What are the main architectural layers?

Answer:

* API: FastAPI routes and request/response schemas.

* Security: authentication, authorization, and tenant context.

* Application: review lifecycle and orchestration entry points.

* Domain: business models, state, and transition rules.

* Retrieval: policy ingestion, embedding, and search.

* AI workflow: planner, supervisor, specialists, evaluator, and HITL.

* Persistence: SQLAlchemy models, repositories, and PostgreSQL.

* Infrastructure: Celery, Redis, Docker, and deployment configuration.

* Cross-cutting: guardrails, configuration, logging, and audit events.

"The goal is to prevent infrastructure concerns from leaking into domain decisions and to make the core behavior independently testable."

## Q7. What is the difference between the API layer and the workflow layer?

Answer:

"The API layer is responsible for accepting requests, validating identity and permissions, and exposing review lifecycle operations.

The workflow layer is responsible for executing the compliance analysis, including retrieval, agent orchestration, evaluation, and human interruption.

I don't want the API endpoint to know how a risk agent works or how a retrieval strategy ranks policies. The API invokes an application-level operation, and the workflow owns the analysis process."

## Q8. What happens when a user submits a review?

Answer:

"The API authenticates the caller, validates the request, creates a review and audit record, commits the database transaction, and submits a Celery task.

The worker loads the review, invokes the LangGraph workflow, retrieves relevant policies, executes the specialist analysis, evaluates the results, validates evidence, and pauses for human approval.

The reviewer decision is later submitted through the API and resumes the workflow using its persisted checkpoint. The final review status and decision are stored in PostgreSQL."

## Q9. What is your most important architectural decision?

Answer:

"The most important decision was to treat this as a governed workflow system with an AI capability inside it, rather than treating the LLM as the application.

The model is not allowed to determine its own permissions, choose arbitrary tools, or finalize the compliance decision. Those responsibilities remain in deterministic application code and the authorized human-review process."

## Q10. What would you change if you were building version two?

Answer:

"I would strengthen the production foundations before adding more agents.

My priorities would be reliable job publication through a transactional outbox, idempotent task processing, consistent state-transition enforcement, production identity integration, PostgreSQL row-level security, semantic evidence evaluation, and restart/resume integration tests.

After that, I would improve hybrid retrieval and reranking based on measured retrieval quality. I would avoid adding architectural complexity without evidence that it improves business outcomes."

# Part 2 — Design patterns and software engineering

## Q11. Which design patterns did you use?

Answer:

"The main patterns are Strategy for interchangeable retrieval algorithms, Repository for persistence abstraction, Dependency Injection for supplying dependencies, Adapter for external embedding providers, and State Machine for the review lifecycle.

At the workflow level, I use graph orchestration, fan-out/fan-in for specialist analysis, and checkpoint/resume for human approval.

These patterns address concrete requirements: changing retrieval implementations, isolating database access, testing components independently, controlling state transitions, and resuming long-running workflows."

## Q12. Explain the Strategy pattern in your project.

Answer:

"I define a common retrieval interface and provide keyword, vector, and fallback implementations.

The workflow uses the retrieval contract instead of depending on a specific search implementation. That means I can introduce a hybrid strategy or another vector provider without rewriting the workflow.

I prefer this over hard-coding retrieval logic into the agent because it separates the decision of how to retrieve evidence from the decision of how to analyze that evidence."

## Q13. Explain the Repository pattern.

Answer:

"The Repository pattern provides an abstraction around persistence operations. Business code can request a review or save an assessment without having to construct every database query itself.

It improves testability and keeps database-specific behavior in one place.

I would also be transparent that the pattern is not applied uniformly everywhere in the current project. Some code still accesses SQLAlchemy directly. In a follow-up refactor, I would establish consistent repository boundaries for the business-critical operations."

## Q14. Why use Dependency Injection?

Answer:

"Dependency Injection allows me to supply database sessions, policy loaders, model clients, and workflow dependencies rather than constructing them throughout the codebase.

For example, a unit test can inject a fake retrieval implementation and test the workflow without contacting PostgreSQL or an embedding provider.

It reduces tight coupling and makes configuration and testing more predictable. I would improve consistency by using a clear composition root for constructing the application dependencies."

## Q15. Explain the Adapter pattern.

Answer:

"The embedding provider adapter converts an external provider's API into an application-defined interface.

The retrieval layer depends on the interface rather than the provider's SDK details. This reduces vendor coupling and makes it easier to substitute a different embedding model.

The adapter does not automatically make two embedding models interchangeable at the data level. Changing embedding models may require re-embedding the policy corpus and managing vector-version compatibility."

## Q16. Why use a State Machine?

Answer:

"A review has a lifecycle, and not every transition is valid. For example, a review should not be approved before it has reached the appropriate review stage.

A state machine makes valid transitions explicit and allows us to test them.

In the current project, the lifecycle definitions and their enforcement need consolidation. I would centralize the state transitions and require all API and worker updates to go through the same validated transition mechanism."

## Q17. What is the difference between a State Machine and LangGraph?

Answer:

"The domain state machine models the business lifecycle: queued, running, awaiting review, approved, rejected, or failed.

LangGraph models the execution of the AI workflow: retrieve, plan, dispatch agents, evaluate, validate, interrupt, and resume.

They are related, but not interchangeable. The domain lifecycle is a business contract, while the graph is an orchestration mechanism. I would keep them aligned through explicit transition rules rather than treating graph node names as the source of business truth."

## Q18. Why use an Adapter instead of directly calling the OpenAI SDK?

Answer:

"Direct SDK calls are simple, but they spread provider-specific request formats, response handling, and error behavior throughout the application.

An adapter gives the application a stable contract. It also provides a natural place to handle timeouts, retries, telemetry, and provider-specific exceptions.

If we later support multiple providers, I would add a model-provider abstraction with capability checks, because not every provider supports identical structured-output or embedding behavior."

## Q19. Which SOLID principles apply?

Answer:

* Single Responsibility: the fee agent analyzes fees; it does not own authorization or persistence.

* Open/Closed: retrieval strategies can be extended behind a stable interface.

* Liskov Substitution: implementations should honor the behavior promised by their common protocols.

* Interface Segregation: agents and repositories should depend on focused contracts.

* Dependency Inversion: high-level workflow logic should depend on abstractions rather than concrete infrastructure.

"I use SOLID as a design guide, not as a reason to create an interface for every class. The abstraction should protect a meaningful boundary or make testing and evolution easier."

## Q20. How do you make the project testable?

Answer:

"I separate the workflow from the API and inject external dependencies where possible. I test deterministic logic independently, including planner task constraints, guardrail validation, RBAC, and state transitions.

For integration tests, I would use real PostgreSQL and Redis in an isolated environment, with controlled model responses where appropriate.

I would also test the complete lifecycle: submit a review, execute it, pause for approval, restart the worker, resume, and verify the persisted result."


# Part 3 — RAG, embeddings, and vector databases

## Q21. Why did you use RAG instead of fine-tuning?

Answer:

"The compliance rules are external knowledge that changes over time. RAG allows the system to retrieve the currently applicable policy passages at inference time.

Fine-tuning is useful for changing model behavior, domain-specific language, or output consistency, but it is not an ideal mechanism for keeping a frequently changing policy database current.

I would first improve retrieval, evidence grounding, and prompt design. I would consider fine-tuning only if an evaluation dataset demonstrated a persistent behavior gap that those approaches could not address."

## Q22. Explain your RAG pipeline.

Answer:

"The ingestion pipeline takes policy content, splits it into chunks, generates embeddings, and stores the text, vector, tenant, policy code, and version in PostgreSQL.

At query time, the system embeds the submitted statement, retrieves semantically similar policy chunks with tenant and active-policy filters, and passes the retrieved evidence to the specialist agents.

The agents generate structured findings with evidence references. The application validates those references against the retrieved source material before presenting the result to a human reviewer."

## Q23. Why do you need embeddings?

Answer:

"Embeddings represent text as numerical vectors that capture aspects of semantic similarity.

A user might say 'guaranteed returns', while a policy might discuss 'assured investment performance'. Keyword matching may not connect those phrases, but vector search can retrieve semantically related passages.

However, embedding similarity is not proof that a policy supports a claim. It is a retrieval mechanism, not a compliance decision mechanism."

## Q24. How does cosine similarity work?

Answer:

"Cosine similarity measures the cosine of the angle between two vectors. It focuses on their direction rather than their magnitude.

For vectors aaa and bbb, it is:

cosine⁡(a,b)=a⋅b∥a∥∥b∥\operatorname{cosine}(a,b)= \frac{a\cdot b}{\|a\|\|b\|}cosine(a,b)=∥a∥∥b∥a⋅b

A larger similarity generally indicates greater semantic closeness for a suitable embedding model.

In pgvector, cosine distance is commonly represented as one minus cosine similarity. The query orders by the smallest distance to find the nearest vectors."

## Q25. Why did you use PostgreSQL with pgvector instead of Qdrant?

Answer:

"PostgreSQL already stores the policy metadata and review records. pgvector lets us store embeddings and perform vector similarity search in the same database, while applying relational filters for tenant and policy status.

That reduces the number of infrastructure components and simplifies consistency.

I would choose a separate vector database such as Qdrant if benchmarks showed that independent vector scaling, indexing capabilities, throughput, or operational isolation justified it. I would make that decision based on measured workload characteristics rather than assuming one database is universally better."

## Q26. Why use keyword fallback?

Answer:

"Vector retrieval can fail because of embedding-provider errors, missing vectors, or an empty result set. Keyword fallback provides another way to retrieve evidence in those cases.

It is a resilience mechanism, but it is not equivalent to a complete hybrid search implementation. In the current design, fallback is sequential: it does not fuse lexical and vector rankings."

## Q27. How would you implement hybrid retrieval?

Answer:

"I would execute lexical and vector retrieval independently, apply the same tenant and policy-version filters, and combine the rankings.

One approach is Reciprocal Rank Fusion, which combines rankings without requiring lexical and vector scores to be directly comparable.

I would then optionally rerank the top candidates with a cross-encoder and evaluate Recall@k, MRR, nDCG, latency, and evidence precision.

I would not add the reranker by default without proving that it improves retrieval quality enough to justify its additional latency and cost."

## Q28. What is chunking, and how did you choose chunk size?

Answer:

"Chunking splits a long policy document into smaller retrievable units. The objective is to retrieve enough context to interpret a rule without sending the entire document to the model.

The current implementation uses fixed-size chunks with overlap. That is a simple baseline.

For production, I would evaluate structure-aware chunking that respects section headings, clauses, and numbered policy rules. I would tune chunk size and overlap using a labeled retrieval dataset, measuring both retrieval recall and whether the returned passage contains sufficient context."

## Q29. How do you handle policy updates and versioning?

Answer:

"I associate policy records with policy identity, version, tenant, and active status. This allows retrieval to target the applicable policy set and gives findings a traceable source.

For production, I would use immutable policy versions, explicit effective dates, an approval process for publishing changes, and a controlled embedding pipeline.

I would also record the exact policy versions used in each review so that historical assessments can be reproduced even after the active policy changes."

## Q30. How would you evaluate RAG quality?

Answer:

"I would evaluate retrieval and generation separately.

For retrieval, I would measure Recall@k, MRR, and nDCG using a labeled set of questions and relevant policy passages.

For generation, I would measure whether findings are supported by the evidence, whether citations are correct, whether material violations are missed, and whether the system abstains when evidence is insufficient.

I would also evaluate the full workflow with human reviewer judgments. A high similarity score or fluent response is not sufficient evidence of compliance accuracy."

# Part 4 — Multi-agent architecture and LangGraph

## Q31. Why use multiple agents instead of one LLM?

Answer:

"I separated the analysis into performance, risk, fees, and general policy responsibilities. Each specialist has a narrower task and returns a structured result.

This can improve observability and make category-specific evaluation easier. It also allows independent tasks to run concurrently.

The trade-off is additional LLM calls, latency, cost, and potential disagreement. I would keep the multi-agent design only if evaluation demonstrates benefits over a single well-designed structured-output call."

## Q32. Explain planner, supervisor, and specialist agents.

Answer:

"The planner creates a bounded set of tasks. The supervisor validates the tasks against an allowlist and controls execution. The specialists perform the actual category-specific analysis.

The planner answers 'what analysis should be performed?' The supervisor answers 'what is allowed to execute?' The specialists answer 'what findings are supported by the supplied evidence?'

In the current project, the planner and supervisor are deterministic. They do not use an LLM to dynamically invent plans or grant themselves new capabilities."

## Q33. Why did you make the planner deterministic?

Answer:

"Compliance workflows benefit from predictable coverage. A deterministic planner creates the required task types, which reduces the risk of skipping a critical category or generating arbitrary work.

An LLM planner could be introduced later if dynamic task decomposition demonstrated measurable value. Even then, its proposed tasks would need schema validation, allowlisting, a step budget, and authorization outside the model."

## Q34. Why have a supervisor if the planner already creates tasks?

Answer:

"The planner defines intended work, while the supervisor enforces execution constraints.

Even if the planner produces valid tasks, the supervisor is a separate control point for checking allowed task types, limiting execution, and rejecting unsupported requests.

This separation becomes especially valuable if planning becomes more dynamic in the future."

## Q35. How do the agents communicate?

Answer:

"They communicate through typed task inputs, structured outputs, and the shared LangGraph workflow state.

The agents do not need to call each other directly. The graph controls the handoffs, which makes execution easier to trace and test.

This is a controlled orchestration model rather than an open-ended network of autonomous agents."

## Q36. What is the difference between MCP and your tool contracts?

Answer:

"MCP is a protocol for exposing tools and resources to compatible AI clients. Our tool contracts define the application-facing inputs, outputs, and permissions for the tools used by this workflow.

The concepts are related, but they are not the same thing. A typed Python tool interface does not automatically mean the project implements an MCP server.

If we exposed policy search or other capabilities through MCP, we would still enforce authentication, tenant scope, input validation, and authorization in the tool implementation."

## Q37. Why not use A2A?

Answer:

"A2A is intended for communication and collaboration between agents or agentic systems. This project primarily uses a centrally controlled workflow, where the graph coordinates specialist calls within one application.

Introducing A2A would add network communication, identity, discovery, and failure-handling concerns without solving a current requirement.

I would consider it if independently deployed agent systems needed to collaborate across organizational or service boundaries."

## Q38. How do you prevent infinite agent loops?

Answer:

"I use a constrained task set, an allowlist of supported task types, and a maximum step budget. The workflow also has bounded evaluation and rework paths.

In production, I would enforce additional limits on wall-clock duration, model calls, tokens, retries, and total cost. I would also detect repeated state transitions and fail safely when the workflow cannot make progress."

## Q39. What happens if one specialist fails?

Answer:

"The orchestration layer must distinguish between a valid negative finding and an execution failure.

A model timeout or provider error should not be interpreted as 'no compliance issue found.' The system should mark the specialist as failed or unavailable and then follow an explicit policy: retry within a limit, use an approved fallback, or fail the review and route it for manual handling.

I would make specialist-level outcomes explicit in the final assessment so missing analysis cannot silently appear as a clean review."

## Q40. Why use `asyncio.gather()`?

Answer:

"The specialist tasks are independent after policy retrieval, so they can execute concurrently.

`asyncio.gather()` allows the workflow to await multiple asynchronous calls together rather than waiting for each agent sequentially.

However, concurrency needs limits. I would use a semaphore or bounded worker pool, enforce provider rate limits, and apply per-agent timeouts. I would also handle each task's exception explicitly so one failed specialist does not get confused with a successful result."

## Q41. How do you control disagreement between agents?

Answer:

"I would not simply let the last agent overwrite the others.

Each specialist returns its own findings with evidence references. The aggregation layer normalizes the outputs, deduplicates equivalent findings, preserves conflicting evidence, and applies deterministic conflict-handling rules.

If specialists disagree about whether a claim is supported, I would retain the disagreement and route it for human review rather than inventing certainty."

## Q42. What is the evaluator responsible for?

Answer:

"The current evaluator checks whether the required specialist outputs are present and whether their evidence references belong to the retrieved policy set.

That is a structural and provenance check, not a complete semantic correctness evaluation.

For a stronger implementation, I would add evidence-entailment evaluation, contradiction checks, category-specific test datasets, and calibrated abstention behavior. I would not rely solely on an LLM judge for high-impact compliance conclusions."

# Part 5 — Guardrails, security, and compliance


## Q43. What are guardrails, and why do you need them?

Answer:

"Guardrails are controls that constrain model inputs, outputs, and actions.

In this project, deterministic guardrails validate the structure of findings, verify that evidence belongs to the correct tenant's retrieved policy set, and check policy identity, version, and exact quoted text.

They address a different problem from prompting. A prompt expresses desired model behavior; a guardrail checks whether the returned result satisfies application-enforced conditions.

I would add further controls for sensitive data, unsupported conclusions, output size, and policy-specific abstention rules."

## Q44. Can your guardrails completely prevent hallucinations?

Answer:

"No. They prevent specific classes of invalid output, but they cannot guarantee that every conclusion is correct.

For example, a model could quote a real policy passage accurately but misinterpret its meaning. The quotation would pass an exact-match check, yet the conclusion could still be unsupported.

I would combine provenance validation with semantic evidence evaluation, adversarial testing, and human review. I would also track false positives and false negatives against a labeled dataset."

## Q45. How do you defend against prompt injection?

Answer:

"I treat the submitted communication and retrieved policy text as untrusted data. The system instructions tell the model not to follow instructions embedded in those documents.

But I do not rely on prompt instructions alone. The application controls tool availability, authorization, tenant scope, and workflow transitions. The model cannot change its own permissions or directly approve a review.

I would also maintain a prompt-injection regression suite containing malicious instructions in both user content and retrieved documents."

## Q46. How do you prevent cross-tenant data leakage?

Answer:

"Tenant identity comes from the authenticated security context, not from the model or an untrusted request field.

The application scopes review and policy queries by tenant. For defense in depth, I would enforce PostgreSQL row-level security with a non-owner runtime role, set tenant context transaction-locally, and test access using the actual production database role.

I would specifically test connection-pool reuse, because a tenant context that is not properly reset could cause serious cross-tenant leakage."

## Q47. How do you implement RBAC?

Answer:

"I associate authenticated principals with roles and enforce permissions at the API and service boundaries.

An analyst may submit a review, a reviewer may make a decision, and a policy administrator may manage policy content. The server checks the required permission before performing the operation.

For production, I would centralize the permission matrix, enforce separation of duties, and test both allowed and denied operations. I would also ensure that hiding a UI action is never treated as authorization."

## Q48. How do you secure the JWT implementation?

Answer:

"I validate the token's signature and relevant claims, including issuer, audience, expiry, and subject. Signing keys must be managed securely and rotated appropriately.

For a production enterprise environment, I would integrate with the organization's identity provider using OIDC/JWKS, define token lifetime and revocation behavior, and consider step-up authentication for sensitive approval actions.

A decoded JWT is not automatically trustworthy; the server must verify it against the expected issuer and signing configuration."

## Q49. How do you protect sensitive financial data?

Answer:

"I would apply data minimization and least privilege at every layer.

That includes encrypting traffic, protecting data at rest, restricting database and object-store access, avoiding sensitive content in logs, and defining retention and deletion policies.

I would also classify data, redact or tokenize sensitive fields where appropriate, and restrict which information is sent to an external model provider. Provider retention and data-processing terms would need to meet the organization's requirements."

## Q50. How do you handle PII in prompts and logs?

Answer:

"I would identify sensitive fields before constructing the model request, redact or tokenize them where possible, and avoid logging full prompts or raw financial documents by default.

Logs should use correlation IDs and structured metadata instead of unnecessary copies of user content.

For debugging, access to sensitive traces should be controlled, audited, and subject to retention limits. Redaction needs testing because naïve patterns can miss or incorrectly modify sensitive data."

## Q51. How do you ensure an LLM cannot approve a review?

Answer:

"The approval decision is a separate, authenticated application operation. The model returns findings, not an authoritative approval.

The server verifies the review's current state, the caller's reviewer permission, tenant scope, and separation-of-duties rules before accepting a decision.

The workflow resumes using the server-validated decision. The LLM does not supply the trusted reviewer identity or grant itself approval permissions."

## Q52. How do you maintain an audit trail?

Answer:

"I record important business events with structured fields such as tenant, actor, entity, action, and timestamp.

For a production audit trail, I would capture the review lifecycle, policy versions, assessment version, reviewer decision, rationale, and relevant model or prompt version identifiers.

I would also protect audit records against unauthorized modification and define retention policies. Operational logs and compliance audit records serve different purposes, so I would not treat them as interchangeable."

## Q53. How do you handle a policy that contains malicious instructions?

Answer:

"I treat retrieved policy content as evidence, not as executable instructions.

The model receives the policy passage within a clearly defined data boundary. Tools and permissions are controlled by application code, and the output must pass validation.

If a policy document is suspected to be compromised, the ingestion and publication process should support quarantine, version rollback, and an audit record. The document should not become trusted simply because it exists in the knowledge base."

# Part 6 — HITL, Celery, Redis, and reliability

## Q54. Explain Human-in-the-Loop in your project.

Answer:

"The workflow reaches a human approval node after analysis and validation. LangGraph interrupts execution and persists the state through its checkpointer.

An authorized reviewer then approves or rejects the proposed assessment. The API validates that decision and queues a resume operation using the same workflow thread.

This allows the review to wait for a human without holding an API request or worker process open."

## Q55. Why not just store `needs_human` in PostgreSQL?

Answer:

"A business status tells us where the review is in its lifecycle, but it does not necessarily preserve the execution state of a complex graph.

The checkpointer stores the workflow state needed to resume from the interruption. PostgreSQL review records and LangGraph checkpoints serve related but distinct purposes.

I would keep them consistent through explicit state transitions and integration tests."

## Q56. What if the reviewer never responds?

Answer:

"I would implement an explicit pending-review policy.

The system should track how long the review has been waiting, send reminders or escalate when appropriate, and support cancellation or expiry where business rules permit.

The review must remain visibly pending rather than being silently treated as approved. The workflow checkpoint and the business record should be retained according to the organization's retention policy."

## Q57. What happens if the worker crashes during a review?

Answer:

"If the graph has persisted a checkpoint, the workflow is designed to resume from that state when the worker becomes available again.

However, I would distinguish checkpoint durability from end-to-end job reliability. We also need to ensure the task can be redelivered, duplicate executions are safe, and the database state is consistent.

I would test worker termination at several points: before graph invocation, during a model call, after the interrupt, and during resume."

## Q58. Why Celery instead of FastAPI BackgroundTasks?

Answer:

"FastAPI BackgroundTasks is convenient for lightweight work attached to a response, but it is not a complete distributed job-processing system.

Celery gives us separate worker processes, broker-backed task delivery, configurable concurrency, and retries. That is more appropriate for potentially long-running AI reviews.

The trade-off is additional infrastructure and the need to handle duplicate delivery, task idempotency, queue monitoring, and broker failures."

## Q59. What is the role of Redis?

Answer:

"Redis acts as the configured Celery broker and result backend. It allows the API to enqueue work and the workers to consume tasks independently.

PostgreSQL remains the system of record for reviews and policies, and it also backs the LangGraph checkpoint in this design.

I would not rely on Redis task results as the only authoritative record of a compliance decision."

## Q60. How do you handle Celery retries?

Answer:

"I would retry transient failures such as connection errors and selected provider timeouts, using bounded retries and exponential backoff with jitter.

I would not blindly retry permanent errors such as invalid input or authorization failures.

Because a task can execute more than once, the review lifecycle must be idempotent. Before writing a result or resuming a graph, the worker should verify the current review state and ensure that the same logical operation has not already completed."

## Q61. What is idempotency, and why is it important here?

Answer:

"An operation is idempotent when repeating it produces the same intended result as performing it once.

Celery may redeliver tasks, and clients may retry requests after a timeout. Without idempotency, the system could create duplicate reviews, duplicate audit events, or apply a reviewer decision more than once.

I would use idempotency keys for review creation, unique decision identifiers, state preconditions, and database constraints where appropriate."

## Q62. What is the transactional outbox pattern?

Answer:

"The transactional outbox solves the dual-write problem between a database and a message broker.

In this project, a review can be committed successfully while publishing the Celery task fails. That leaves a queued review with no corresponding job.

With an outbox, the API writes both the review and an outbox event in one PostgreSQL transaction. A separate publisher delivers pending events to the broker and marks them as published.

Delivery may still occur more than once, so consumers must be idempotent. The outbox provides reliable publication, not magical exactly-once execution."

## Q63. How would you scale the workers?

Answer:

"I would scale the Celery workers independently from the API based on queue depth, task wait time, worker utilization, and downstream model limits.

I would use bounded concurrency to avoid overwhelming the LLM provider or database. I would also consider separate queues for different workload classes, such as policy ingestion and interactive reviews.

Autoscaling should consider both throughput and queue age, not just CPU utilization, because workers may spend much of their time waiting on external APIs."

## Q64. How do you handle rate limits from the LLM provider?

Answer:

"I would implement provider-aware concurrency limits, bounded retries for rate-limit responses, exponential backoff with jitter, and request timeouts.

I would monitor request rate, token rate, error rate, and retry volume. If the provider is overloaded, the system should slow down or queue work rather than amplify the problem with aggressive retries.

I would also define a maximum number of model calls and a cost budget per review."

## Q65. What happens if Redis is unavailable?

Answer:

"The API should not claim that a review has been successfully queued if task publication has failed.

With the current commit-then-publish flow, this is a failure mode that needs explicit handling. A transactional outbox would allow the review and the intent to enqueue it to be committed together, with delivery retried when Redis recovers.

Operationally, I would alert on broker connectivity, queue age, and the number of pending outbox events."


# Part 7 — Database, APIs, and distributed systems

## Q66. Explain your database schema.

Answer:

"The main business entities are policies, reviews, and audit events.

A policy stores the tenant, policy identifier, version, text, and embedding. A review stores the submitted content, lifecycle status, and assessment. Audit events record important operations.

For production, I would make policy versions immutable, define explicit relationships and constraints, and ensure the review records preserve the exact policy versions used during analysis."

## Q67. Why SQLAlchemy?

Answer:

"SQLAlchemy provides ORM mapping, query construction, transaction management, and async database integration. It lets the application work with domain-oriented objects while retaining access to SQL when needed.

I would use explicit transaction boundaries and avoid holding database sessions open during long LLM calls. Long-running external operations should not keep a database connection occupied unnecessarily."

## Q68. Why use Alembic?

Answer:

"Alembic versions database schema changes as migrations. That makes database evolution repeatable across development, staging, and production.

I would run migrations as a controlled deployment step, review destructive changes carefully, and use an expand-and-contract approach for schema changes that must be compatible with multiple application versions."

## Q69. How would you implement PostgreSQL row-level security?

Answer:

"I would enable RLS on tenant-owned tables and define policies that compare the row's tenant ID against a transaction-local tenant context.

The application would connect using a non-owner role that cannot bypass RLS. Tenant context would be set inside each transaction and reset automatically at transaction completion.

I would test both permitted and forbidden queries with the real application role, including connection-pool reuse and background workers. RLS is defense in depth; application-level tenant filtering remains useful."

## Q70. How do you prevent SQL injection?

Answer:

"I use parameterized SQL and SQLAlchemy's expression APIs rather than interpolating untrusted input into SQL strings.

For vector search and raw SQL, I would bind query values as parameters and carefully validate any dynamic identifiers or ordering expressions, since SQL identifiers cannot always be handled like ordinary values.

I would also run the application with least-privilege database permissions."

## Q71. How do you design a reliable review API?

Answer:

"I would define explicit request and response schemas, authenticate and authorize every operation, and give each review a stable identifier.

Review creation should support idempotency. Long-running operations should return an accepted response and a way to poll status. Decision endpoints should enforce state preconditions and prevent duplicate decisions.

I would also use consistent error contracts, request correlation IDs, rate limits, and audit events."

## Q72. Why return HTTP 202 Accepted?

Answer:

"Because the review has been accepted for asynchronous processing, but the analysis is not necessarily complete.

The response can contain the review ID and a status URL. The client can poll the review resource or use an event-driven notification mechanism.

Returning 200 with a completed result would be misleading if the worker has not finished the analysis."

## Q73. How would you design API idempotency?

Answer:

"I would accept an idempotency key for review creation and store it with the authenticated tenant and relevant request identity under a uniqueness constraint.

If the same request is retried with the same key, the API returns the existing review instead of creating another one.

I would define how conflicting payloads using the same key are handled and how long the key is retained."

## Q74. How do you handle database transactions around Celery tasks?

Answer:

"I would keep database transactions short and avoid holding them open during model calls.

The review record and outbox event should be committed atomically. A publisher then sends the task. The worker opens its own session, loads the review, and commits state changes at controlled points.

I would avoid passing live ORM sessions or database objects through Celery. Tasks should carry serializable identifiers and reload the required data."

## Q75. How do you avoid race conditions when two reviewers submit decisions?

Answer:

"I would enforce a state precondition and use a database transaction with an optimistic version check or row-level locking.

Only one decision should transition a review from the pending state. A second conflicting request should receive a conflict response rather than overwrite the first decision.

I would also record the actor and decision ID so retries of the same decision can be handled idempotently."

# Part 8 — LLM evaluation, observability, and production operations

## Q76. How do you measure whether the AI system is accurate?

Answer:

"I would maintain a representative, expert-labeled evaluation dataset with policy versions, submitted statements, expected findings, and supporting evidence.

I would measure category-level precision and recall, severity calibration, evidence support, citation validity, and abstention behavior.

I would evaluate retrieval separately from generation and then measure end-to-end reviewer outcomes. Aggregate accuracy alone can hide a serious failure in a high-risk category."

## Q77. How do you measure hallucination?

Answer:

"I would define a hallucination operationally as a material claim that is unsupported by the supplied evidence or contradicts the applicable source.

I would sample model findings and have qualified reviewers label whether the cited evidence supports each claim. I would report unsupported-finding rates, citation mismatch rates, and severity-weighted error rates.

An LLM judge can help scale evaluation, but I would calibrate it against human labels and not treat it as ground truth."

## Q78. What is the difference between precision and recall in compliance review?

Answer:

"Precision measures how many flagged findings are valid. Recall measures how many actual issues in the labeled dataset the system identifies.

Low precision means reviewers spend time investigating false alarms. Low recall means the system misses issues.

Both matter. The acceptable operating point depends on the business risk and the cost of missed findings versus additional manual reviews."

## Q79. How do you evaluate a new prompt or model version?

Answer:

"I would run it against a fixed offline evaluation dataset and compare it with the current baseline.

I would examine changes in recall, precision, evidence support, severity classification, latency, and cost. I would also run adversarial and regression tests.

For a production rollout, I would use versioned prompts and models, a staged deployment, and a rollback mechanism. If feasible, I would compare versions in shadow mode before allowing the new version to influence reviewer-facing decisions."

## Q80. What is your observability strategy?

Answer:

"I would correlate the API request, Celery task, LangGraph execution, database operations, and model calls using trace and review identifiers.

I would collect structured logs, distributed traces, and metrics for latency, errors, queue depth, model usage, token cost, and workflow outcomes.

Sensitive content should not be included in telemetry by default. Observability needs to support debugging while respecting data minimization and access controls."

## Q81. Which metrics would you put on a production dashboard?

Answer:

"I would organize metrics into four categories.

* Service health: API availability, error rates, p95/p99 latency.

* Queue health: queue age, pending jobs, task retries, worker utilization.

* AI performance: model latency, timeout rate, tokens, cost, retrieval latency.

* Compliance quality: evidence validity, unsupported findings, reviewer overrides, unresolved reviews, and missed-issue rate on labeled evaluations.

I would set service-level objectives for both operational reliability and review turnaround, with separate quality gates for model behavior."

## Q82. How would you set SLOs?

Answer:

"I would define SLOs from user and business needs rather than selecting arbitrary numbers.

For example, API acceptance latency should be short because it does not include the full AI analysis. Review completion time needs a separate target, measured from submission to a reviewable assessment. Human waiting time should be reported separately from machine processing time.

I would define availability and error budgets for the API and worker pipeline, then validate proposed thresholds using actual workload measurements."

## Q83. How would you reduce LLM cost?

Answer:

"I would start by measuring cost per review and identifying which agents or prompts contribute most.

Potential improvements include retrieving fewer but more relevant chunks, avoiding duplicate embedding calls, caching safe reusable computations, using smaller models for low-risk tasks, and reducing redundant agent calls.

I would not optimize cost at the expense of missing important compliance issues. Any model or retrieval change would have to pass the evaluation suite."

## Q84. How would you reduce latency?

Answer:

"I would separate queue wait time, retrieval time, model time, evaluation time, and human waiting time.

For machine-processing latency, I would parallelize independent specialists, optimize vector retrieval, use bounded concurrency, and avoid repeated embedding or model calls.

I would also set timeouts and budgets so that a slow dependency cannot hold the workflow indefinitely. The target should be end-to-end latency at a defined workload, not simply the fastest individual model call."

## Q85. How would you deploy this to AWS?

Answer:

"I would deploy the API and Celery workers as separate containerized workloads.

A possible design is ECS or EKS for compute, RDS PostgreSQL with pgvector for persistent data, and a managed Redis-compatible service for the broker. I would use a secrets manager, private networking, IAM roles, centralized logs, and infrastructure as code.

I would first validate the exact pgvector extension and indexing support on the chosen database service, as well as the LangGraph checkpoint behavior. I would not choose Kubernetes automatically; ECS may be simpler if the organization does not need Kubernetes-specific capabilities."

## Q86. How would you support high availability and disaster recovery?

Answer:

"I would define recovery-point and recovery-time objectives with the business.

For PostgreSQL, I would configure backups, point-in-time recovery, and tested restoration procedures. For Redis, I would select persistence and recovery settings appropriate to its role as a broker. I would also make pending work recoverable through the outbox and task-reconciliation process.

I would test restoration, worker recovery, and workflow resumption rather than assuming that configured backups or checkpoints guarantee successful recovery."

# Part 9 — Staff-level architecture and design judgment


## Q87. How would you handle millions of review requests?

Answer:

"I would first establish the workload profile: requests per second, average and tail processing time, document sizes, model rate limits, and peak concurrency.

The API would scale independently from the workers. Celery queues would absorb bursts, and worker autoscaling would respond to queue age and backlog. PostgreSQL would need appropriate indexing, connection pooling, query optimization, and potentially partitioning for high-volume audit data.

I would introduce admission control, per-tenant quotas, and backpressure to prevent overload. I would also benchmark the complete pipeline, because scaling the API alone does not increase the throughput of a rate-limited LLM provider."

## Q88. How would you prevent one tenant from consuming all the capacity?

Answer:

"I would implement per-tenant quotas and fair scheduling.

That could include limits on concurrent reviews, requests per minute, document size, token budgets, and total daily usage. Separate queues or weighted scheduling could prevent a large tenant from starving smaller tenants.

I would monitor queue age and resource consumption by tenant. The objective is predictable service quality while maintaining isolation and cost control."

## Q89. How would you handle a model provider outage?

Answer:

"I would use bounded retries with backoff, circuit breaking, and explicit failure states.

If an approved alternative provider is available, I would route to it only after validating that it supports the required output contract, privacy requirements, and quality threshold.

I would not silently fall back to a weaker model and present the result as equivalent. If no acceptable provider is available, the review should remain incomplete or be routed to manual processing."

## Q90. How would you make the system reproducible?

Answer:

"I would record the input document hash, policy IDs and versions, retrieval configuration, embedding model version, prompt version, LLM model identifier, workflow version, and final reviewer decision.

I would also preserve the relevant evidence and structured assessment under the organization's retention policy.

Even with those records, exact reproduction of an LLM response may not always be possible because provider models can change. The goal is to preserve the information needed to explain and audit the original decision."

## Q91. How would you roll out a new model safely?

Answer:

"I would version the model configuration and run offline evaluations first. I would then use a staged rollout, potentially with shadow traffic, to compare the new model against the current version.

I would monitor evidence support, category-level recall, severity errors, latency, and cost. The rollout would have explicit acceptance thresholds and a rollback path.

For high-impact changes, I would require compliance-owner sign-off before allowing the new model to influence reviewer-facing assessments."

## Q92. How would you handle a policy conflict?

Answer:

"I would not let vector similarity alone determine which policy wins.

The retrieval layer should return policy identity, version, effective date, and applicable scope. A deterministic policy-resolution component should apply approved precedence rules, such as effective dates, jurisdiction, product scope, and authoritative policy hierarchy.

If the applicable policies genuinely conflict or the precedence is unclear, the system should preserve the conflicting evidence and escalate the issue for human resolution."

## Q93. How would you make findings explainable?

Answer:

"Each finding should contain the statement being assessed, the finding category, severity, rationale, and references to the exact supporting policy passages.

The reviewer should be able to inspect the policy code, version, and source text. I would distinguish direct evidence from the model's interpretation and make uncertainty visible.

Explainability here means traceable reasoning and evidence—not claiming that a natural-language explanation perfectly exposes the model's internal reasoning."

## Q94. How would you handle an incorrect human approval?

Answer:

"I would preserve the original decision as an immutable audit event and provide a controlled correction or superseding-decision process.

The system should record who made the correction, when it occurred, why it was made, and which assessment and policy versions were involved.

I would also feed appropriately governed reviewer corrections into the evaluation dataset. I would not silently overwrite the historical record because that would compromise auditability."

## Q95. What would you do if the LLM returned valid JSON but incorrect findings?

Answer:

"Schema validation only proves that the response conforms to the expected structure. It does not prove that the findings are true.

I would check whether the evidence supports the conclusion, whether the policy applies to the product and jurisdiction, and whether the model has confused a warning with a violation.

The finding would either be rejected, marked uncertain, or routed for additional review according to the applicable policy. I would add the example to the regression dataset to prevent recurrence."

## Q96. How do you decide whether to add another agent?

Answer:

"I would identify a distinct analytical responsibility that is not adequately handled by the existing specialists.

Then I would compare a single-agent baseline against the proposed multi-agent design using the same evaluation set. I would measure quality, latency, cost, operational complexity, and failure behavior.

I would add the agent only if the improvement justifies the additional complexity. A new agent should have a clear contract, bounded permissions, test coverage, and an explicit place in the workflow."

## Q97. What is the biggest technical risk in your project?

Answer:

"The biggest risk is producing a plausible but incorrect compliance finding, particularly when the evidence is incomplete, outdated, or interpreted incorrectly.

That risk is not solved by using more agents. It requires authoritative policy management, correct retrieval, version-aware evidence, semantic evaluation, controlled abstention, and human oversight.

Operationally, I would also treat tenant isolation and reliable workflow resumption as critical requirements because failures there can affect confidentiality or leave reviews in inconsistent states."

## Q98. What would you prioritize if you had only one month before production?

Answer:

"I would prioritize risk reduction over new features.

First, I would complete identity-provider integration, authorization reviews, tenant isolation, and separation of duties. Second, I would fix reliable task publication, idempotency, and lifecycle transition enforcement. Third, I would validate checkpoint recovery and establish the minimum quality evaluation and operational monitoring required for a controlled rollout.

I would then run security testing, failure-injection tests, load testing, and a limited pilot with human reviewers. I would not launch broadly until the acceptance criteria were met."

## Q99. What did you learn from building this project?

Answer:

"The biggest lesson is that an enterprise AI system is much more than an LLM and a vector database.

The difficult engineering problems are workflow reliability, evidence provenance, authorization, evaluation, and human accountability.

I also learned that architectural complexity needs to be justified. Multi-agent orchestration, vector search, and checkpointing are useful only when they solve concrete requirements and can be tested and operated reliably."

## Q100. Why is this a Senior or Staff AI Engineer project?

Answer:

"I would position it as a senior/staff-level reference implementation because it brings together AI engineering, distributed systems, backend architecture, security, and workflow governance.

The design demonstrates explicit separation of concerns, controlled agent execution, retrieval abstraction, durable workflow state, and human approval.

I would distinguish the architectural scope from production maturity. To call it production-ready, I would need to demonstrate the security controls, reliability guarantees, evaluation quality, and operational recovery through testing and deployment evidence—not just the presence of the frameworks."

# Part 10 — Questions about ownership, decisions, and trade-offs

These questions often distinguish a senior engineer from someone who has only studied the code.

## Q101. What was your personal contribution?

Answer template — adapt this to what you actually built:

"I was responsible for the design and implementation of the core compliance-review workflow. My work covered the API and service boundaries, retrieval design, agent contracts, workflow orchestration, guardrails, and human approval lifecycle.

I also evaluated the architectural trade-offs around persistence, asynchronous processing, and tenant isolation. Where the implementation still needs production hardening, I have identified the gaps and defined the engineering work required to address them."

Only claim the responsibilities you personally performed. If this is a personal project or a reference implementation, say so clearly.

## Q102. What was the hardest engineering problem?

Answer:

"The most challenging problem was coordinating probabilistic AI analysis with deterministic workflow and security requirements.

The agents may produce incomplete or conflicting findings, while the application must still enforce tenant isolation, preserve state, and prevent unauthorized approval.

I addressed this by separating analysis from orchestration and placing deterministic validation and human approval around the model-generated results. The remaining challenge is proving those guarantees under real failures and adversarial inputs."

## Q103. Tell me about a design decision you would reverse.

Answer:

"One area I would strengthen is the separation between database state and workflow state.

The review lifecycle and the LangGraph execution state are related, but they are not the same thing. I would establish one authoritative lifecycle transition service and make API and worker updates use it consistently.

I would also introduce an outbox for job publication. That would remove the gap between committing a review and successfully scheduling its processing."

## Q104. What would you do if the team disagreed with your architecture?

Answer:

"I would start by making the requirements and constraints explicit, then compare the options against those requirements.

For example, if the team preferred a simpler single-LLM workflow, I would build a baseline and compare quality, latency, and cost against the multi-agent design.

I would document the decision and its trade-offs, choose the simplest design that meets the requirements, and revisit the decision when evidence changes."

## Q105. How would you mentor another engineer on this project?

Answer:

"I would explain the system from the business workflow inward rather than starting with framework details.

I would walk through one request, identify the responsibility of each layer, and then trace the key interfaces and state transitions. I would ask the engineer to implement or test one bounded component, such as a retrieval strategy or a guardrail, and review the design reasoning as well as the code.

The goal would be to help them understand why the boundaries exist, not just how to call the APIs."

## Q106. How would you know whether the project is delivering business value?

Answer:

"I would establish a baseline for manual review time, review turnaround, reviewer disagreement, and the quality of documented evidence.

Then I would compare the assisted workflow against that baseline using a representative set of reviews. I would track both productivity and quality, including false positives, missed issues, and reviewer overrides.

The project would only be successful if it improves the review process without reducing the quality or accountability of compliance decisions."

# Part 11 — A live architecture walkthrough you can practice

If the interviewer says, "Draw the architecture and explain it," use this sequence.

1

Start with the business requirement

"We need to review financial statements against versioned policies and produce evidence-backed findings for an authorized human."

2

Draw the request path

"FastAPI authenticates and authorizes the caller, persists the review, and queues the task through Celery."

3

Draw retrieval

"The worker retrieves tenant-scoped, versioned policy evidence from PostgreSQL and pgvector."

4

Draw the graph

"The planner creates bounded tasks, the supervisor controls execution, and specialist agents analyze different claim categories."

5

Draw validation and HITL

"The evaluator checks coverage, deterministic guardrails validate evidence, and LangGraph pauses for human approval."

6

Finish with reliability

"PostgreSQL persists business records and checkpoints. I would harden the system with outbox delivery, idempotency, RLS, and restart/resume tests."

## The five statements to remember

1. "The model analyzes; application code authorizes."

2. "Retrieval finds candidate evidence; it does not prove compliance."

3. "The business state machine and the AI workflow graph serve different purposes."

4. "A persisted status is not the same as a resumable workflow checkpoint."

5. "Production readiness must be demonstrated through security, reliability, and quality tests."

## How to prepare efficiently

### Interview preparation checklist

0 of 10

Practice the 2-minute project introduction

Draw the architecture from memory

Explain the full request-to-approval flow

Explain Strategy, Repository, DI, and State Machine

Explain pgvector, chunking, retrieval, and evaluation

Explain planner, supervisor, specialists, and fan-out/fan-in

Explain HITL interrupt, checkpoint, and resume

Practice tenant isolation, RBAC, and prompt-injection answers

Explain Celery retries, idempotency, and transactional outbox

Review the production gaps and how you would address them

Reset checklist
x
Final advice: Don't try to memorize all 106 answers word for word. Learn the architecture, understand the trade-offs, and practice answering with one concrete example from the project. For every major design choice, be ready to explain three things: why you chose it, what alternative you rejected, and what you would change if the system had to operate at enterprise scale.
