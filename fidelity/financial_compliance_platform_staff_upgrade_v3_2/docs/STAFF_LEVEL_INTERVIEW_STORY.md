# Staff-level interview narrative

## 90-second project explanation

I designed a financial-services compliance and risk review platform that turns an advisor's proposed communication or investment-related statement into an evidence-backed, auditable review case. The core engineering problem is not simply retrieving a paragraph from a vector database. It is making a high-impact decision-support workflow reliable, tenant-isolated, explainable and recoverable when models, workers or external dependencies fail.

The API accepts a review command and persists the review, audit event and outbox event atomically. An asynchronous worker starts a LangGraph workflow using a stable server-generated thread ID and a PostgreSQL-backed checkpoint. The workflow retrieves tenant-scoped, versioned policy context, creates bounded specialist tasks, executes relevant analyses concurrently, evaluates completeness and evidence references, applies deterministic guardrails, and pauses for a human reviewer. A reviewer decision is authorized independently, checked against the lifecycle state and separation-of-duties rule, then resumes the same graph. The final decision and audit trail are persisted.

The important design principle is that the LLM is not the control plane. It can propose analysis, but deterministic code controls tenant scope, permissions, task allowlists, retry budgets, state transitions and approval. The system uses at-least-once event delivery with idempotent processing rather than assuming a queue gives exactly-once execution.

## Deep-dive: why not one large agent?

A single agent with broad tools creates an unpredictable permission and loop surface. I separated orchestration from specialist reasoning. The graph owns state transitions; the supervisor validates bounded tasks; specialists return typed outputs; the evaluator checks evidence coverage; guardrails validate policy provenance; and a human owns the final decision. Deterministic operations such as arithmetic, authorization and lifecycle transitions remain ordinary code.

## Deep-dive: reliability and duplicate processing

The review row, audit event and outbox event are committed together. The publisher may deliver an event more than once, so the worker uses stable review/thread identity, task/lease controls and idempotent state transitions. If a worker crashes, the queue can redeliver and the graph can resume from its checkpoint. The design does not claim exactly-once message delivery; it makes repeated delivery safe at the business-operation boundary.

## Deep-dive: tenant isolation

Tenant identity is derived from the authenticated principal, never from prompt text or model output. Repository queries include tenant scope and PostgreSQL RLS provides a second enforcement layer. Runtime connections must use a non-owner role without BYPASSRLS. The important validation is integration testing with that exact role and pooled connections to detect tenant-context leakage.

## Deep-dive: retrieval correctness

The current implementation combines lexical and vector retrieval using reciprocal-rank fusion and exposes a keyword fallback when vector retrieval fails. That improves recall across exact policy terms and semantic paraphrases, but it does not prove that a claim is entailed by a policy. The next correctness layer is a reranker, claim-level evidence ledger, contradiction checks, semantic entailment benchmark and abstention threshold. I would report retrieval recall and citation precision separately from answer quality.

## Deep-dive: how to scale

Scale API and worker fleets independently. Use queue backpressure, per-tenant quotas, provider concurrency limits, bounded graph steps, async I/O, database pool budgets and cache keys that include tenant and policy version. Measure p95/p99 latency, queue wait, provider latency, token cost, retrieval recall, error rate and reviewer SLA. I would not promise a request-per-second number until load and failure testing establish it.

## Difficult questions and concise answers

**Why LangGraph instead of a chain?** The process has durable state, conditional routing, bounded rework and a human interrupt/resume lifecycle. A simple chain is preferable for a linear one-shot task.

**Why Celery if LangGraph has checkpoints?** Checkpoints preserve workflow state; the task queue provides asynchronous dispatch, worker concurrency, retries and operational backpressure. They solve different problems.

**Why PostgreSQL and pgvector?** Transactional case/audit data and vector retrieval can share tenant-aware governance and operational ownership at this scale. A separate vector service becomes justified when measured corpus size, QPS, isolation or recall requirements exceed this design.

**How do you stop agent loops?** The graph owns transitions, task types are allowlisted, maximum steps and rework counts are persisted, and terminal states cannot be reopened through ordinary commands.

**What if the LLM provider is down?** Apply request deadlines, bounded retries, circuit breaking and a declared fallback policy. If evidence quality cannot be maintained, fail closed or queue for later; do not silently turn a deterministic keyword match into an LLM conclusion.

**How do you prevent prompt injection?** Treat submitted documents and retrieved passages as untrusted data, separate instructions from data, expose only narrow read-only tools, validate tool arguments and permissions in code, and run regression tests against an injection corpus.

**How do you know the answer is correct?** Provenance checks establish where evidence came from, not whether it supports a claim. Correctness needs claim-level adjudicated datasets, entailment/contradiction metrics, numerical validation, abstention and reviewer override analysis.

**What would you do next as Staff engineer?** Establish measurable quality and reliability gates, prioritize the evidence ledger and semantic evaluation, define service ownership and SLOs, and phase in identity, document intelligence and financial-data integrations behind governed interfaces.

## Do not overclaim

The supplied code is an advanced reference implementation, not proof of a regulated production deployment. Describe implemented mechanisms as implemented; describe OIDC, OCR, market-data adapters, portfolio stress tests, Kafka, full OpenTelemetry and production-scale throughput as roadmap until code, tests and deployment evidence exist.
