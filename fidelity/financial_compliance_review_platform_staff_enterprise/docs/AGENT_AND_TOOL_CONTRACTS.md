# Agent, tool, and handoff contracts

## Agent responsibilities
- **Planner:** emits a bounded set of typed tasks; cannot authorize capabilities.
- **Supervisor:** validates task kind against an allowlist, caps steps/rework, and routes work.
- **Specialists:** perform narrow analysis and return typed findings with evidence references.
- **Evaluator:** checks completeness and evidence coverage; can request bounded rework.
- **Guardrail gate:** deterministic validation before any human sees a recommendation.
- **Human reviewer:** the only actor allowed to approve/reject the proposed compliance outcome.

## Tool boundary
Every tool must declare: name, input schema, permission, tenant source, timeout, side-effect class,
audit event, and error contract. Tenant identity is injected from the authenticated principal, never
from an LLM-generated argument. Default to read-only tools. Model output is untrusted input.

## Handoffs
The graph—not an agent prompt—owns handoffs. A specialist returns a result; the supervisor decides
whether to continue, retry, rework, fail closed, or escalate to a human. No unbounded agent loops.
