# Financial AI Modular Platform

A Staff/Senior-level modular monorepo/reference implementation for two enterprise AI
applications built on reusable platform packages.

Applications:
- financial-compliance
- investment-intelligence

Shared packages:
- platform-core
- platform-auth
- platform-db
- platform-cache
- platform-messaging
- platform-observability
- ai-llm
- ai-rag
- ai-agents
- ai-guardrails

## Architecture

```text
Client
  |
  v
FastAPI
  |
  v
Application Service / Use Case
  |
  +-----------------------------+
  | Domain / Business Rules     |
  +-----------------------------+
  |
  v
Ports / Contracts
  |
  +----------------+----------------+----------------+
  |                |                |                |
Postgres         Redis             LLM              RAG
Adapter          Adapter           Adapter          Adapter
```

The most important rule:

> Shared packages contain reusable technical capabilities.
> Applications contain business/domain-specific behavior.

This is a modular monolith/monorepo, not a premature microservice decomposition.
Each application can later be deployed independently.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
make install
make test

cp .env.example .env

make run-compliance
# http://localhost:8001/docs

make run-investment
# http://localhost:8002/docs
```

The reference uses a deterministic MockLLM, so it does not require an external model key.


I created the modular Staff/Senior-level reference project with **85 files**.

### Download

[**Download the complete modular Financial AI platform ZIP**](sandbox:/mnt/data/financial_ai_modular_platform_staff_reference.zip)

The project is structured so you can clearly see **what belongs in reusable packages vs. what belongs inside each business application**.

---

# 1. Overall architecture

The generated project follows this model:

```text
financial_ai_modular_platform/
│
├── packages/                         # REUSABLE PLATFORM
│   │
│   ├── platform-core/
│   ├── platform-auth/
│   ├── platform-db/
│   ├── platform-cache/
│   ├── platform-messaging/
│   ├── platform-observability/
│   │
│   ├── ai-llm/
│   ├── ai-rag/
│   ├── ai-agents/
│   └── ai-guardrails/
│
├── applications/                    # BUSINESS APPLICATIONS
│   │
│   ├── financial-compliance/
│   │
│   └── investment-intelligence/
│
├── deployments/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── docs/
│   └── architecture/
│
├── tests/
│
├── Makefile
├── pyproject.toml
├── .env.example
└── README.md
```

The most important architectural principle is:

```text
                  REUSABLE PLATFORM
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
   Auth / DB          AI / RAG         Agents
   Redis              LLM              Guardrails
   Messaging          Observability
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                 BUSINESS APPLICATIONS
                         │
              ┌──────────┴──────────┐
              │                     │
       Compliance App        Investment App
```

---

# 2. Why we are creating packages

Previously your two projects had duplication.

For example, both projects need:

```text
FastAPI
PostgreSQL
Redis
authentication
RBAC
LLM
RAG
agents
guardrails
logging
observability
Celery
```

There is no reason to implement these twice.

Instead:

```text
                    ai-llm
                      ↑
                      │
Compliance ───────────┤
                      │
Investment ───────────┘
```

Both applications import the same package.

For example:

```python
from ai_llm.factory import create_llm
```

Both applications can use it.

---

# 3. `platform-core`

```text
packages/platform-core/

├── pyproject.toml
└── src/platform_core/
    ├── __init__.py
    ├── errors.py
    └── types.py
```

This is the **lowest-level shared package**.

It contains things like:

```python
class AppError(Exception):
    pass

class ValidationError(AppError):
    pass

class AuthorizationError(AppError):
    pass

class NotFoundError(AppError):
    pass
```

Why?

Because every application may need common errors.

But you should **not** put:

```text
ComplianceViolation
PortfolioRisk
MarketingPolicy
InvestmentRecommendation
```

inside `platform-core`.

Those belong to applications.

---

# 4. `platform-auth`

```text
packages/platform-auth/

└── src/platform_auth/
    ├── __init__.py
    ├── models.py
    ├── rbac.py
    └── dependencies.py
```

This package owns generic authentication/authorization infrastructure.

For example:

```python
@dataclass(frozen=True)
class Principal:
    subject: str
    tenant_id: str
    roles: frozenset[str]
```

And:

```python
class RBAC:
    def authorize(
        self,
        principal: Principal,
        permission: str
    ):
        ...
```

The important distinction is:

### Shared

```text
JWT validation
Principal
Tenant context
RBAC engine
Permission checking
```

### Application

Compliance:

```text
review:create
review:approve
policy:manage
```

Investment:

```text
portfolio:read
portfolio:analyze
research:approve
```

So the shared package provides the **mechanism**.

The application provides the **business permissions**.

---

# 5. `platform-db`

```text
packages/platform-db/

└── src/platform_db/
    ├── __init__.py
    ├── session.py
    └── uow.py
```

This is where generic PostgreSQL/SQLAlchemy infrastructure goes.

For example:

```python
class Database:
    def __init__(self, dsn):
        self.engine = create_async_engine(...)
        self.sessions = async_sessionmaker(...)
```

And transaction management:

```python
async with transaction(session):
    ...
```

But this package should NOT contain:

```text
ComplianceReviewRepository
PolicyRepository
PortfolioRepository
MarketDataRepository
```

Those belong to the application.

Why?

Because repositories contain **business meaning**.

---

# 6. Repository pattern

The architecture should eventually become:

```text
Application Service
       |
       v
ComplianceReviewRepository
       |
       | interface / port
       v
SQLAlchemyComplianceReviewRepository
       |
       v
PostgreSQL
```

For investment:

```text
InvestmentService
       |
       v
PortfolioRepository
       |
       v
SQLAlchemyPortfolioRepository
       |
       v
PostgreSQL
```

The database package supplies the infrastructure.

The application owns the repository.

That's an important Staff Engineer distinction.

---

# 7. `platform-cache`

```text
packages/platform-cache/

└── src/platform_cache/
    └── cache.py
```

This contains reusable Redis mechanics.

For example:

```python
await cache.set_json(
    "review:123",
    result,
    ttl_seconds=300
)
```

But this package should not know:

```text
review:123
portfolio:123
compliance:policy:123
```

Those keys are application concepts.

---

# 8. `platform-messaging`

```text
packages/platform-messaging/

└── src/platform_messaging/
    ├── celery.py
    └── events.py
```

This provides:

```text
Celery
events
task infrastructure
message configuration
```

For example:

```python
create_celery(
    name="financial-ai",
    broker_url="redis://localhost:6379/1"
)
```

But the business task belongs to the application.

For example:

```text
financial-compliance
    tasks/
        review_document.py

investment-intelligence
    tasks/
        market_research.py
```

not:

```text
platform-messaging/
    compliance_task.py    ❌
```

---

# 9. `platform-observability`

```text
packages/platform-observability/

└── src/platform_observability/
    ├── logging.py
    ├── context.py
    └── metrics.py
```

This is cross-cutting infrastructure.

Eventually this is where you would integrate:

```text
OpenTelemetry
Prometheus
structured logging
trace IDs
correlation IDs
workflow IDs
LLM token metrics
LLM cost
latency
errors
```

For example:

```text
trace_id
workflow_id
tenant_id
request_id
agent_name
model
input_tokens
output_tokens
latency_ms
```

That information should be consistent across both applications.

---

# 10. `ai-llm`

This is one of the most important packages.

```text
packages/ai-llm/

└── src/ai_llm/
    ├── __init__.py
    ├── ports.py
    ├── mock.py
    └── factory.py
```

The central abstraction is:

```python
class LLMProvider(Protocol):

    async def generate(
        self,
        request: LLMRequest
    ) -> LLMResponse:
        ...
```

Now your application doesn't care whether the model is:

```text
OpenAI
Anthropic
AWS Bedrock
Azure OpenAI
Llama
vLLM
local model
mock
```

The application says:

```python
response = await llm.generate(request)
```

rather than:

```python
openai.chat.completions.create(...)
```

This is the **Adapter pattern**.

---

# 11. Why the LLM abstraction is important

Imagine your compliance application currently uses OpenAI.

Six months later:

```text
OpenAI
   ↓
AWS Bedrock
```

Without abstraction:

```text
ComplianceService
      |
      v
OpenAI SDK
```

You need to rewrite business code.

With the architecture:

```text
ComplianceService
      |
      v
LLMProvider
      |
      +------ OpenAIAdapter
      |
      +------ BedrockAdapter
      |
      +------ AnthropicAdapter
```

Only the adapter changes.

That's exactly why we use **Ports & Adapters / Hexagonal Architecture**.

---

# 12. `ai-rag`

```text
packages/ai-rag/

└── src/ai_rag/
    ├── models.py
    ├── ports.py
    ├── pipeline.py
    └── in_memory.py
```

This package contains reusable RAG infrastructure.

For example:

```text
Document
Chunk
Evidence
Embedder
Retriever
Reranker
```

The important part is:

```python
class Retriever(Protocol):

    async def retrieve(
        self,
        query: str,
        top_k: int = 5
    ) -> list[Evidence]:
        ...
```

Now we can have:

```text
Retriever
    │
    ├── VectorRetriever
    ├── BM25Retriever
    ├── HybridRetriever
    └── QdrantRetriever
```

or:

```text
Retriever
    │
    └── PgVectorRetriever
```

The application doesn't need to know how retrieval works.

---

# 13. RAG strategy pattern

This is where your previous **Strategy pattern** discussion becomes useful.

For example:

```python
class Retriever(Protocol):
    ...
```

Implementations:

```text
VectorRetriever
BM25Retriever
HybridRetriever
```

Then:

```text
                     Retriever
                         │
            ┌────────────┼────────────┐
            │            │            │
          Vector        BM25        Hybrid
```

You can configure:

```text
RETRIEVAL_STRATEGY=hybrid
```

without rewriting your business workflow.

That's the **Strategy pattern**.

---

# 14. `ai-agents`

This is another critical package.

```text
packages/ai-agents/

└── src/ai_agents/
    ├── contracts.py
    ├── runtime.py
    ├── checkpoint.py
    └── workflow.py
```

It provides generic agent concepts:

```text
Agent
Planner
Supervisor
Evaluator
AgentContext
AgentResult
AgentRuntime
Checkpoint
Workflow
```

But it does NOT contain:

```text
ComplianceResearchAgent
FeeAgent
PortfolioAgent
MarketResearchAgent
PolicyAgent
```

Those belong to applications.

---

# 15. Planner vs Supervisor

This distinction is extremely important for your interviews.

### Planner

The planner answers:

> What work needs to be done?

Example:

```text
User asks:
"Review this marketing document."

Planner:

1. retrieve policies
2. identify claims
3. analyze claims
4. classify risk
5. generate rationale
6. evaluate
7. request approval if needed
```

The planner creates the plan.

---

### Supervisor

The supervisor answers:

> What should happen next?

For example:

```text
retrieve
   |
   v
analyze
   |
   v
evaluate
   |
   +---- quality good ----> finish
   |
   +---- quality poor ----> retry
```

So:

```text
Planner = WHAT work?
Supervisor = WHAT NEXT?
```

---

# 16. Evaluator / rework loop

Your generated architecture includes the evaluator contract.

Production flow:

```text
                  Specialist Agents
                         |
                         v
                     Evaluator
                         |
             ┌───────────┴───────────┐
             │                       │
          PASS                      FAIL
             │                       │
             v                       v
          Continue                 Rework
                                     |
                                     v
                                Evaluator
                                     |
                                  retries
                                     |
                                  exceeded
                                     |
                                     v
                                    HITL
```

This is much stronger than:

```python
if result:
    return result
```

because enterprise AI needs a quality-control loop.

---

# 17. Checkpointing

`ai-agents/checkpoint.py` demonstrates the concept:

```text
Workflow
   |
   v
Checkpoint
   |
   v
PostgreSQL
```

For the real production implementation, this should become something like:

```text
LangGraph
    |
    v
Postgres Checkpointer
```

Then:

```text
workflow
   |
   v
high-risk decision
   |
   v
INTERRUPT
   |
   v
persist state
   |
   |
   |  human decision later
   |
   v
RESUME
   |
   v
workflow continues
```

This is proper HITL.

---

# 18. `ai-guardrails`

```text
packages/ai-guardrails/

└── src/ai_guardrails/
    ├── models.py
    ├── engine.py
    └── validators.py
```

Shared guardrails can include:

```text
prompt injection
PII
empty input
schema validation
unsafe output
citation requirements
hallucination checks
```

But financial business rules remain application-specific.

For example:

```text
ai-guardrails
    └── PromptInjectionValidator
```

while:

```text
financial-compliance
    └── GuaranteedReturnClaimValidator
```

---

# 19. Financial Compliance application

Now we reach the actual business application:

```text
applications/financial-compliance/

├── src/financial_compliance/
│   ├── main.py
│   ├── domain/
│   │   └── models.py
│   ├── agents.py
│   └── services/
│       └── review_service.py
│
├── tests/
└── pyproject.toml
```

This application owns:

```text
financial compliance
policy review
risk classification
compliance agents
compliance workflow
HITL decisions
compliance repositories
compliance policies
```

---

# 20. Compliance request flow

For:

```http
POST /v1/reviews
```

the flow is:

```text
FastAPI
   |
   v
Principal
   |
   v
ComplianceReviewService
   |
   +---- Guardrails
   |
   +---- Risk classification
   |
   +---- Compliance Research Agent
   |
   +---- RAG
   |
   +---- LLM
   |
   +---- Writer Agent
   |
   +---- HITL if high risk
   |
   v
Response
```

This is what you should be able to explain in an interview.

---

# 21. Investment Intelligence application

The second application:

```text
applications/investment-intelligence/

├── src/investment_intelligence/
│   ├── main.py
│   ├── domain/
│   │   └── models.py
│   ├── agents.py
│   └── services/
│       └── analysis_service.py
│
└── tests/
```

It can use the same:

```text
platform-auth
platform-db
platform-cache
platform-messaging
platform-observability

ai-llm
ai-rag
ai-agents
ai-guardrails
```

But it has its own:

```text
MarketResearchAgent
InvestmentWriterAgent
InvestmentQuestion
Portfolio rules
Market policies
Investment repositories
```

---

# 22. This is the important part

You now have:

```text
                   SHARED PLATFORM
                         │
        ┌────────────────┼─────────────────┐
        │                │                 │
        v                v                 v
   platform-*         ai-llm            ai-rag
        │                                  │
        │                              ai-agents
        │                                  │
        │                            ai-guardrails
        │                                  │
        └────────────────┬─────────────────┘
                         │
             ┌───────────┴────────────┐
             │                        │
             v                        v
     Compliance App           Investment App
```

Therefore, if tomorrow you create:

```text
insurance-ai
```

you don't need to rewrite:

```text
authentication
Redis
Celery
LLM abstraction
RAG
agent runtime
guardrails
observability
```

You simply create:

```text
applications/insurance-ai/
```

and import the packages.

---

# 23. What happens when a third application comes?

Suppose you create:

```text
Wealth Management Copilot
```

You create:

```text
applications/
    wealth-management/
```

and:

```python
from ai_llm.factory import create_llm
from ai_agents.contracts import AgentContext
from ai_guardrails.engine import GuardrailEngine
```

Then build:

```text
WealthAdvisorAgent
PortfolioAgent
SuitabilityAgent
TaxAgent
```

inside the application.

You don't copy:

```text
ai-llm/
ai-rag/
ai-agents/
ai-guardrails/
```

again.

---

# 24. Where LangGraph fits

The generated project intentionally isolates the generic agent contracts.

For your **full production version**, I recommend:

```text
ai-agents/
    src/ai_agents/
        contracts/
        runtime/
        checkpoint/
        langgraph_adapter/
```

Then:

```text
Application
     |
     v
AgentRuntime
     |
     v
LangGraph Adapter
     |
     v
StateGraph
```

The application defines the actual graph:

```text
START
  |
  v
Planner
  |
  v
Supervisor
  |
  +----------+
  |          |
  v          v
Research   Analysis
  |          |
  +----+-----+
       |
       v
    Evaluator
       |
   +---+---+
   |       |
 PASS     FAIL
   |       |
   v       v
 HITL    Rework
   |
   v
 END
```

That keeps LangGraph from leaking into every business class.

---

# 25. What goes into `packages/`

Think of `packages/` as your **internal enterprise AI platform**.

```text
packages/
│
├── platform-core
│
├── platform-auth
│
├── platform-db
│
├── platform-cache
│
├── platform-messaging
│
├── platform-observability
│
├── ai-llm
│
├── ai-rag
│
├── ai-agents
│
└── ai-guardrails
```

These should answer:

> "How do we technically implement this capability?"

---

# 26. What goes into `applications/`

Applications answer:

> "What does this business actually do?"

For compliance:

```text
financial-compliance
```

For investment:

```text
investment-intelligence
```

They contain:

```text
domain
business policies
use cases
agents
workflow definitions
repositories
application APIs
application-specific prompts
application-specific guardrails
```

---

# 27. The dependency direction

This is one of the most important things to remember:

```text
                APPLICATION
                     |
                     v
              APPLICATION SERVICE
                     |
                     v
                  DOMAIN
                     |
                     v
                   PORT
                     |
                     v
                 ADAPTER
                     |
                     v
              INFRASTRUCTURE
```

Never do this:

```text
Domain
  |
  v
FastAPI        ❌
```

or:

```text
Domain
  |
  v
OpenAI SDK     ❌
```

or:

```text
Domain
  |
  v
SQLAlchemy     ❌
```

Instead:

```text
Domain
   |
   v
Port
   ^
   |
Adapter
   |
   v
Infrastructure
```

That's the essence of **Hexagonal / Ports & Adapters**.

---

# 28. How I would evolve this into your final enterprise projects

The ZIP I generated is the **architecture/reference foundation**. For your actual resume-grade versions, I would evolve it to:

```text
packages/
│
├── platform-core
├── platform-auth
├── platform-db
├── platform-cache
├── platform-messaging
├── platform-observability
│
├── ai-llm
│   ├── openai
│   ├── bedrock
│   ├── anthropic
│   ├── routing
│   └── structured_output
│
├── ai-rag
│   ├── ingestion
│   ├── chunking
│   ├── embeddings
│   ├── pgvector
│   ├── qdrant
│   ├── bm25
│   ├── hybrid
│   └── reranking
│
├── ai-agents
│   ├── runtime
│   ├── planner
│   ├── supervisor
│   ├── evaluator
│   ├── handoffs
│   ├── tools
│   ├── checkpointing
│   └── langgraph
│
└── ai-guardrails
    ├── prompt_injection
    ├── pii
    ├── schema
    ├── hallucination
    ├── citation
    └── policy
```

Then:

```text
applications/
│
├── financial-compliance/
│   ├── domain/
│   ├── application/
│   ├── agents/
│   ├── workflows/
│   ├── repositories/
│   ├── adapters/
│   ├── api/
│   ├── workers/
│   └── migrations/
│
└── investment-intelligence/
    ├── domain/
    ├── application/
    ├── agents/
    ├── workflows/
    ├── repositories/
    ├── adapters/
    ├── api/
    ├── workers/
    └── migrations/
```

That is the structure I would recommend you use for the **final Staff AI Engineer portfolio version**.

---

## The single rule I want you to remember

When you're unsure where a class/module belongs, ask:

> **"Is this technology/business capability reusable by another unrelated application?"**

If yes:

```text
packages/
```

If no:

```text
applications/<business-domain>/
```

For example:

```text
LLMProvider                    → packages/ai-llm
PostgresSession                → packages/platform-db
RedisClient                    → packages/platform-cache
PromptInjectionValidator      → packages/ai-guardrails

ComplianceReview              → applications/financial-compliance
ComplianceResearchAgent       → applications/financial-compliance
MarketingClaimPolicy          → applications/financial-compliance

PortfolioAnalysis             → applications/investment-intelligence
MarketResearchAgent            → applications/investment-intelligence
PortfolioRiskPolicy            → applications/investment-intelligence
```

That separation is what turns your two projects from **two large application repositories** into a **reusable enterprise AI platform with multiple bounded-context applications**.
