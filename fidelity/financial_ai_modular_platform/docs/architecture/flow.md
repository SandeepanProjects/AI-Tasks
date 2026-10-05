# End-to-end flow

## Compliance request

```text
POST /v1/reviews
      |
      v
FastAPI route
      |
      v
Principal / tenant
      |
      v
ComplianceReviewService
      |
      +--> Guardrails
      |
      +--> Domain risk classification
      |
      +--> Compliance Research Agent
      |       |
      |       +--> RAG / policy retrieval
      |
      +--> LLM Provider
      |
      +--> Writer Agent
      |
      +--> HITL if high risk
      |
      v
Response / persisted workflow state
```

## Planner vs Supervisor

Planner asks:
> What work needs to be done?

Example:
1. retrieve policies
2. analyze claims
3. classify risk
4. generate rationale
5. evaluate
6. request approval

Supervisor asks:
> Given the current state, what should happen next?

Example:

```text
retrieve -> analyze -> evaluate
                       |
                  quality low?
                  /                        retry       continue
```

## Evaluator / rework

```text
agents
  |
  v
evaluator
  |
  +-- pass --> continue
  |
  +-- fail --> rework --> evaluator
                         |
                    max retries
                         |
                       HITL
```

## HITL

HITL should be a workflow state transition:

```text
workflow
   |
high-risk decision
   |
checkpoint/interrupt
   |
human approve/reject
   |
resume
```

It is not merely a boolean in an API response.

## Repository

```text
Service
  |
  v
Repository Port
  |
  v
SQLAlchemy Repository Adapter
  |
  v
PostgreSQL
```

## Strategy

```text
Retriever
  +-- VectorRetriever
  +-- BM25Retriever
  +-- HybridRetriever
```

## Adapter

```text
LLMProvider
  +-- OpenAIAdapter
  +-- BedrockAdapter
  +-- AnthropicAdapter
  +-- MockLLM
```
