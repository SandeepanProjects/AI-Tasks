# Staff-level upgrade blueprint

## Product definition

**Enterprise Financial Intelligence, Compliance & Risk Management Platform**

An auditable decision-support platform for financial-services teams. It ingests governed financial documents and approved data feeds, evaluates advisory content and portfolio scenarios against versioned policy, detects risk and conflicting evidence, and routes decisions through role-separated human approval. It is decision support, not autonomous investment advice or a replacement for a compliance officer.

> Fidelity positioning: describe this as a financial-services platform designed around controls expected in a large regulated enterprise. Do not claim it is Fidelity's internal architecture, uses proprietary Fidelity systems, or was deployed at Fidelity unless that is verifiably true.

## What exists in the supplied 3.1.0 codebase

- FastAPI API, PostgreSQL persistence, SQLAlchemy and Alembic migrations.
- Tenant-aware data access and PostgreSQL row-level security scaffolding.
- JWT/RBAC permission checks.
- LangGraph workflow with planner, supervisor, four specialist roles, evaluator, deterministic guardrails and durable interrupt/resume seam.
- Parallel specialist execution and bounded evaluation rework.
- pgvector plus lexical retrieval with reciprocal-rank fusion and keyword fallback.
- Celery/Redis asynchronous processing, transactional outbox, idempotency keys and worker leases.
- Review lifecycle, creator/reviewer separation of duties and audit events.
- Docker Compose, tests and operational documentation.

## Priority gaps found during code inspection

1. Planner is a fixed list of up to four specialist tasks; it is not content-adaptive planning.
2. Specialists are narrow LLM wrappers with a deterministic phrase-matching fallback. There is no independent financial-data/tool research layer.
3. Ingestion accepts extracted text, uses character slicing, and does not yet implement PDF/OCR, document classification, table extraction, malware scanning or source connector authorization.
4. Hybrid retrieval is RRF over vector and keyword results. A cross-encoder reranker, query rewriting, metadata filters, parent-child retrieval and retrieval benchmark are not present.
5. Evaluator verifies coverage and evidence references; exact quote validation does not prove semantic entailment, numerical correctness or absence of contradictions.
6. Full OpenTelemetry traces/metrics/exporters, SLO dashboards, tenant budgets, rate limits, provider circuit breakers and DLQ operations are still documented production work.
7. OIDC/JWKS and enterprise identity lifecycle are not implemented; current local JWT/RBAC is a seam, not enterprise SSO.
8. No complete portfolio analytics, market-data adapter, policy change-impact engine or case-management integration exists yet.

## Target architecture

```text
Advisor / Compliance UI / API clients
                |
     API Gateway + OIDC/JWKS + WAF
                |
  FastAPI command/query API (tenant context)
       |                 |
 PostgreSQL           Transactional outbox
 review/case/audit          |
 policy metadata       Event publisher
       |                    |
 Document intake       Kafka or managed queue
       |                    |
 AV scan -> parser -> OCR -> layout/table extraction
       -> PII classification -> document classifier
       -> canonical sections -> policy version registry
       -> chunk + embed -> pgvector / object storage
                            |
                  LangGraph orchestration
                            |
       Adaptive planner -> policy/safety supervisor
          |          |           |           |
      Policy      Claims      Portfolio    Regulatory
      analyst     verifier    risk agent    research agent
          |          |           |           |
          +------ approved read-only tool gateway ------+
             policy KB | market data | portfolio API
             CRM | document repository | regulatory feed
                            |
       Hybrid retrieval -> reranker -> evidence ledger
                            |
       Independent evaluator / contradiction checker
       numerical validator / risk scoring / abstention
                            |
          deterministic policy and security guardrails
                            |
           durable HITL approval / escalation queue
                            |
        decision record + immutable audit + notifications
                            |
             monitoring / feedback / model evaluation
```

## Capabilities to implement, in order

### P0 — Make the existing workflow genuinely intelligent and defensible

1. **Adaptive task planning**: classify the submission, extract claims/entities, estimate risk, then create only the required specialist tasks. Use a typed plan schema, allowed task catalogue, max task count, deadline and token budget. The supervisor—not the LLM—validates every task and controls transitions.
2. **Evidence ledger**: every finding references document ID, version, page, section, chunk ID, source offsets, retrieval score and quote hash. Persist evidence separately from free-form model prose.
3. **Independent claim verification**: split submissions into atomic claims; verify each against retrieved evidence; label supported, contradicted, insufficient evidence or out-of-scope. Require abstention when evidence is weak.
4. **Contradiction detection**: compare claims against multiple policy versions and approved source documents; surface conflicting clauses and effective dates rather than silently choosing one.
5. **Numerical validation**: parse percentages, fees, returns, dates and currency values into typed values; recompute arithmetic and compare against approved source data. Do not let an LLM be the calculator or source of truth.
6. **Risk engine**: deterministic, versioned rules combine severity, customer impact, claim type, evidence confidence and policy criticality. The LLM may explain, but cannot set permissions or override the risk policy.
7. **Reviewer packet**: concise executive summary, claim-by-claim findings, cited evidence, policy versions, uncertainty, risk rationale, model/prompt versions and recommended action. Reviewer can approve, reject, request changes or escalate.

### P1 — Financial-services domain depth

8. **Portfolio exposure analysis**: approved read-only adapter for holdings, asset allocation, concentration, sector/country exposure, liquidity and volatility. Include data timestamp, freshness SLA and missing-data handling.
9. **Scenario and stress testing**: deterministic scenario engine for rate shocks, equity drawdowns, FX changes and asset-specific shocks. Clearly label assumptions; no unsupported forecasts.
10. **Market and research intelligence**: source allowlist, licensed market-data adapter, source provenance, freshness checks and sentiment as a weak signal—not a trading instruction.
11. **Policy change-impact analysis**: compare new policy versions, identify changed clauses, map them to prior findings/approved content, and open reassessment cases.
12. **Case management**: queues, assignment, SLA timers, escalation, reviewer workload, reassignment, comments and decision history.

### P2 — Enterprise integration and scale

13. OIDC/JWKS SSO, SCIM lifecycle, step-up authentication for high-risk decisions, centralized authorization and secrets/KMS integration.
14. Connectors for SharePoint/document management, CRM, approved market data, internal policy repositories and case-management tools. Use read-only tools by default and per-tool permission scopes.
15. Event streaming for ingestion/review lifecycle, schema versioning, replay, DLQ, deduplication and consumer lag monitoring.
16. Full OpenTelemetry traces across API -> queue -> worker -> graph -> provider -> database; RED metrics, token/cost metrics, tenant quotas, SLOs and alerts.
17. Model gateway with provider routing, timeout budgets, circuit breakers, fallback policy, prompt/model registry and controlled rollout.
18. Evaluation and governance: offline golden datasets, retrieval recall@k, nDCG, citation precision, claim entailment, false-positive/negative rates, reviewer override rate, drift and canary evaluation.
19. Data lifecycle: retention schedules, legal hold, deletion workflows, encryption/key rotation, backup/PITR and tested disaster recovery.
20. Resilience: load/soak tests, fault injection, queue backlog recovery, provider outage drills, database failover and checkpoint restart/resume tests.

## Critical design choices interviewers should hear

- **Workflow vs agents:** deterministic workflow for lifecycle, authorization, retries and approvals; agents only for bounded reasoning tasks where ambiguity exists. Do not use an agent for simple extraction, routing, arithmetic or CRUD.
- **LLM trust boundary:** model output is untrusted. It cannot choose tenant IDs, permissions, SQL, arbitrary URLs, approval state or side-effecting tools.
- **Tool gateway:** each tool declares schema, permission, tenant source, timeout, rate limit, side-effect class, audit event and error contract. Enforce policy outside the prompt.
- **Durability:** persist command + outbox in one DB transaction; publish at least once; use idempotent consumers. Graph state is checkpointed; never hold DB transactions open while calling an LLM or waiting for a human.
- **Multi-tenancy:** tenant identity comes from verified identity claims; enforce tenant scope in repositories and PostgreSQL RLS. Test using a non-owner, non-BYPASSRLS role.
- **Retrieval:** metadata filters first, hybrid lexical/vector retrieval, reranking, source freshness/version constraints, then evidence validation. Fallback must be visible and measured.
- **Human governance:** separation of duties, step-up auth, rationale, reviewer identity, assessment version and append-only audit record.
- **Scale:** horizontally scale stateless APIs and workers independently; bound concurrency per provider and tenant; use queue backpressure, connection-pool budgets and caching only for safe, tenant-scoped data.

## Suggested service/module boundaries

- `identity`: OIDC/JWKS, principals, permission policy, step-up auth.
- `document_intelligence`: parsing, OCR, classification, PII/DLP, canonical document model.
- `policy_registry`: policy versions, effective dates, supersession, change diff and impact graph.
- `retrieval`: query planning, hybrid search, reranker, evidence ledger.
- `claim_analysis`: atomic claim extraction, entailment, contradiction, numerical validation.
- `portfolio_analytics`: read-only portfolio adapter and deterministic risk/scenario engine.
- `orchestration`: LangGraph state machine, planner, supervisor, bounded specialists, evaluator, HITL.
- `case_management`: queues, SLA, assignments, decisions and escalations.
- `eventing`: outbox, publisher, consumers, idempotency, DLQ and replay.
- `model_gateway`: provider abstraction, budgets, routing, retries, circuit breaker and telemetry.
- `governance`: audit, retention, evaluation datasets, model/prompt registry and release gates.

## Acceptance criteria before claiming implementation

- Adaptive planner tests prove irrelevant agents are not run and required agents cannot be skipped.
- Prompt-injection corpus proves document text cannot change tool permissions, tenant scope or workflow state.
- Evidence tests verify page/section/offset and exact policy version, not merely a matching policy ID.
- Claim benchmark reports precision/recall and abstention; human reviewers adjudicate the test set.
- Numerical tests cover rounding, units, currency, dates, missing values and contradictory inputs.
- Tenant-isolation tests run against real PostgreSQL with the production-like non-owner role.
- Restart tests kill workers between checkpoint/interrupt/resume and verify exactly one business decision.
- Provider outage tests validate timeout, circuit breaker, fallback and queue recovery.
- Load tests state throughput, p95/p99 latency, error rate, token cost and resource limits; do not claim millions of requests without measurements.
- Security review covers SSO, secrets, encryption, retention, audit immutability, dependency scanning and penetration testing.

## Truthful resume positioning

Use only bullets for features actually implemented and tested. Current code can support bullets about LangGraph orchestration, hybrid retrieval, bounded rework, HITL, tenant-aware RBAC/RLS scaffolding, outbox/idempotency and audit lifecycle. Do not yet claim OCR, portfolio stress testing, market-data integrations, OIDC, Kafka, cross-encoder reranking, full OTel, production millions-of-requests scale or regulatory certification.

## Revision 3.2.0 implementation update

The seven capability areas now have concrete reference modules and tests/assets. The adaptive planner is wired into the existing graph. Document intake, evidence/semantic evaluation, portfolio analytics, policy impact, enterprise identity/connectors and telemetry are available as isolated components with explicit integration boundaries. See `SEVEN_STAFF_CAPABILITIES_STATUS.md` for what is and is not connected to the live API/graph. Do not describe standalone components as end-to-end production workflows until their integration steps are completed and verified.
