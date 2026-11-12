# Seven staff-level capability areas — implementation status

This file distinguishes executable code from architecture that still needs environment-specific integration. The platform is a reference implementation and must not be described as a deployed Fidelity system.

| # | Capability | Added in this revision | Runtime status / boundary |
|---|---|---|---|
| 1 | Adaptive multi-agent planner and supervisor | Content-signal planner, task allowlist, bounded task budget, planner adapter wired into LangGraph plan node, evaluator now checks selected specialists | Adaptive selection is active for the four existing specialist agents. Portfolio/regulatory specialist agents are not dispatched by the current graph. |
| 2 | Advanced document intelligence and ingestion | PDF/text/HTML intake, size/type validation, content classification, scanned-PDF OCR provider contract, provenance-aware chunking | New intake module is not yet wired to an authenticated upload API, malware scanner, object store or a production OCR vendor. Existing policy API remains text-based. |
| 3 | Evidence ledger, semantic evaluator and contradiction detection | Evidence record/hash model, tenant-scoped SQL repository, append-only intent, RLS migration, semantic judge contract + OpenAI structured judge, confidence-based abstention and pairwise contradiction API | Evidence persistence is available as a repository component; claim extraction and semantic judge are not yet inserted into the main LangGraph path. Judge output is advisory and must remain behind deterministic guardrails. |
| 4 | Financial portfolio analytics and stress testing | Deterministic allocation/concentration summaries and linear scenario sensitivity engine | Standalone domain module; no live portfolio provider, valuation normalization, covariance model, options/nonlinear repricing or financial advice. |
| 5 | Policy change impact analysis | Version diff and keyword-based candidate matching to historical artifacts, human reassessment flag | Candidate generator only; it does not autonomously reopen or approve cases. Historical artifact query/persistence and semantic mapping require integration. |
| 6 | Enterprise integrations, security and observability | Read-only connector contract, HTTPS host allowlist, permission check, OIDC/JWKS verifier, optional OTLP trace bootstrap | No actual SharePoint/CRM/market-data connector credentials or IdP configuration supplied. OTEL exporter must be configured; existing JWT remains the active API auth until the verifier is integrated at the gateway. |
| 7 | Performance, load and fault-injection testing | Locust script, staging fault-drill plan, measurable test protocol | Assets are added but tests have not been run against a live staging environment. No capacity/SLO claim is made. |

## Suggested integration order

1. Wire document intake to a tenant-authorized upload command, malware scanning, encrypted object storage and asynchronous parsing.
2. Persist evidence records in the same tenant transaction as review outputs; add claim extraction and semantic evaluation nodes before deterministic guardrails.
3. Add approved portfolio and market-data adapters with data freshness contracts; expose the portfolio stress service as a read-only tool.
4. Persist policy-version diffs and reassessment cases; notify case management through the outbox.
5. Configure enterprise OIDC/JWKS, tool-level authorization, OpenTelemetry collector/exporter and alert rules.
6. Run integration, load, soak, failover and fault-injection suites in staging; record measured results before stating throughput or availability.

## Safety and governance boundaries

- LLM-generated assessments are not legal determinations or investment recommendations.
- Market and portfolio data must be licensed, tenant-authorized, timestamped and freshness-checked.
- Stress results are deterministic scenario sensitivities, not forecasts or VaR unless a validated methodology is added.
- Policy impact matches are candidates for reassessment; a qualified reviewer owns the final decision.
- The LLM cannot choose tenant identity, grant permissions, invoke arbitrary URLs, or approve a case.
