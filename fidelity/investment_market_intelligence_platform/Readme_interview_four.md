# 1. Understand the big picture first

These five concepts solve different problems in an enterprise AI system. They are not competing architectures; they can work together in the same application.

Imagine you're building your Financial Compliance Review Platform. An advisor submits a document, and the system must retrieve policies, analyze claims, identify risks, evaluate the result, and possibly ask a human reviewer to approve it.

Here is how the concepts fit together:

FastAPI / API layer

Receives the request

Application / use-case layer

Uses ports to communicate with databases, AI providers and other external systems

Hexagonal architecture

Repository

Loads and saves reviews, policies and results

Adapters

Connect ports to PostgreSQL, an LLM, Redis, etc.

Workflow orchestration

Planner

Supervisor

Chooses and coordinates the work

Specialists

Evaluator

Analyze the document, check the result, and request bounded rework if needed

Conceptual architecture—not a claim that every box is implemented identically in both of your projects.

A useful way to remember them:

| Concept                        | Main question it answers                                                            |
| ------------------------------ | ----------------------------------------------------------------------------------- |
| Hexagonal / Ports and Adapters | How do I keep business logic independent of infrastructure?                         |
| Adapter                        | How do I connect an external technology to my application?                          |
| Strategy                       | How do I swap one algorithm or behavior for another?                                |
| Planner–Supervisor             | How do I decide what work is needed and coordinate it?                              |
| Repository                     | How does application code access and persist data without knowing database details? |
| Evaluator / rework loop        | How do I check a result and improve it when it fails?                               |

Let's understand each one from the ground up.

# 2. Hexagonal Architecture / Ports and Adapters

## 2.1 The problem it solves

Suppose you write a compliance service like this:

Python

Run

```
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

class ComplianceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = AsyncOpenAI()

    async def review(self, document: str):
        # Query PostgreSQL directly
        # Call OpenAI directly
        # Apply compliance rules
        # Save the result directly
        ...
```

At first, this looks straightforward. But the service now knows about:

* PostgreSQL and SQLAlchemy

* OpenAI's SDK

* How to retrieve policies

* How to run compliance checks

* How to save results

What happens if you want to replace OpenAI with Azure OpenAI? Or use a mock LLM during testing? Or replace PostgreSQL with another storage implementation?

You may need to change the same business service every time the infrastructure changes.

Hexagonal architecture addresses this coupling.

## 2.2 The core idea

Your business logic defines what it needs, but does not dictate which external technology must provide it.

There are three important pieces:

Core / application logic

The use cases and business rules. For example, “review this marketing document against the applicable policies.”

Ports

Interfaces describing what the core needs, such as saving a review, retrieving policies, or generating an analysis.

Adapters

Concrete implementations that connect those interfaces to PostgreSQL, an LLM API, a vector database, or another system.

The key dependency rule is:

The application depends on abstractions (ports), not directly on infrastructure implementations.

## 2.3 A concrete Python example

Imagine the application needs an LLM to analyze a document.

First, define a port:

Python

Run

```
# application/ports.py

from typing import Protocol


class ComplianceAnalyzer(Protocol):
    async def analyze(
        self,
        document: str,
        policies: list[str],
    ) -> dict:
        ...
```

This is a contract. It says that any compatible analyzer must provide an asynchronous `analyze()` method with this input and output shape.

Now the application service depends on that contract:

Python

Run

```
# application/review_service.py

class ReviewService:
    def __init__(self, analyzer: ComplianceAnalyzer):
        self.analyzer = analyzer

    async def review(
        self,
        document: str,
        policies: list[str],
    ) -> dict:
        return await self.analyzer.analyze(
            document=document,
            policies=policies,
        )
```

Notice what is missing: there is no OpenAI import, no Azure SDK, and no database code.

Now implement an adapter:

Python

Run

```
# infrastructure/openai_adapter.py

class OpenAIComplianceAdapter:
    def __init__(self, client):
        self.client = client

    async def analyze(
        self,
        document: str,
        policies: list[str],
    ) -> dict:
        response = await self.client.responses.create(
            model="your-configured-model",
            input=(
                f"Review this document:\n{document}\n"
                f"Applicable policies:\n{policies}"
            ),
        )

        return {"analysis": response.output_text}
```

The adapter translates your application's request into the external provider's API call.

Finally, wire the implementation at the application's composition root:

Python

Run

```
client = create_openai_client()

analyzer = OpenAIComplianceAdapter(client)
review_service = ReviewService(analyzer)
```

The composition root is where the application chooses the concrete implementation. In a production system, configuration and dependency injection typically handle this wiring.

### What did we gain?

The same service can now use a different adapter:

Python

Run

```
review_service = ReviewService(
    analyzer=AzureOpenAIComplianceAdapter(azure_client)
)
```

Or a fake analyzer in a unit test:

Python

Run

```
class FakeAnalyzer:
    async def analyze(self, document, policies):
        return {"analysis": "Test result"}
```

The core service does not need to change.

## 2.4 Why is it called “hexagonal”?

The hexagon is a diagramming metaphor, not a requirement to have six components.

* The inside is your application.

* The edges are ports.

* The outside contains adapters and external systems.

An external system can connect through a port, regardless of whether it is a database, web API, queue, file system, or user interface.

There are also two common directions:

* Inbound / driving adapters: bring requests into the application. Examples: FastAPI routes, CLI commands, message consumers.

* Outbound / driven adapters: let the application reach external systems. Examples: PostgreSQL repositories, LLM clients, Redis cache, vector-store clients.

## 2.5 How this maps to your Investment project

Your Investment Market Intelligence project has an application layer with ports and use cases. Its workflow and storage dependencies are represented through abstractions, while concrete API, database, and provider implementations sit outside the core.

That is the architectural intent: keep the use case separate from the technology used to execute it.

Important: Hexagonal architecture does not mean “we have interfaces, so we are enterprise-ready.” The dependencies must actually follow the intended direction. If your business service imports SQLAlchemy, creates an OpenAI client, and performs direct infrastructure calls, the separation is weakened even if the repository contains a `ports.py` file.

# 3. Adapter vs Strategy

These two are often confused because both can involve interchangeable implementations. But they solve different problems.

## 3.1 Adapter pattern: make two interfaces compatible

Imagine your application expects this interface:

Python

Run

```
class MarketDataProvider(Protocol):
    async def get_price(self, symbol: str) -> float:
        ...
```

But an external market-data SDK exposes something different:

Python

Run

```
class VendorSDK:
    async def fetch_quote(self, ticker: str) -> dict:
        ...
```

The application expects `get_price()` returning a number. The vendor gives you `fetch_quote()` returning a dictionary.

An adapter bridges that mismatch:

Python

Run

```
class VendorMarketDataAdapter:
    def __init__(self, sdk: VendorSDK):
        self.sdk = sdk

    async def get_price(self, symbol: str) -> float:
        quote = await self.sdk.fetch_quote(ticker=symbol)
        return float(quote["last_price"])
```

The adapter translates:

* Method name: `get_price` → `fetch_quote`

* Argument: `symbol` → `ticker`

* Return type: dictionary → float

* Potentially errors, authentication, and provider-specific details

Remember: Adapter is about compatibility.

## 3.2 Strategy pattern: select an interchangeable behavior

Now suppose you support three ways to rank retrieved policies:

1. Keyword ranking

2. Vector similarity ranking

3. Hybrid ranking

The application wants to call the same operation, but the algorithm differs.

Python

Run

```
class RankingStrategy(Protocol):
    async def rank(self, query: str, documents: list) -> list:
        ...
```

Implement different strategies:

Python

Run

```
class KeywordRanking:
    async def rank(self, query, documents):
        # Rank using keyword overlap
        return keyword_rank(query, documents)


class VectorRanking:
    async def rank(self, query, documents):
        # Rank using embedding similarity
        return vector_rank(query, documents)


class HybridRanking:
    async def rank(self, query, documents):
        # Combine keyword and vector scores
        return hybrid_rank(query, documents)
```

Then inject the selected strategy:

Python

Run

```
class PolicyRetriever:
    def __init__(self, ranking: RankingStrategy):
        self.ranking = ranking

    async def retrieve(self, query, documents):
        return await self.ranking.rank(query, documents)
```

Configuration can select the strategy:

Python

Run

```
retriever = PolicyRetriever(
    ranking=HybridRanking()
)
```

Remember: Strategy is about choosing behavior.

## 3.3 The difference in one table

|                        | Adapter                                            | Strategy                                          |
| ---------------------- | -------------------------------------------------- | ------------------------------------------------- |
| Main purpose           | Make an external interface fit your port           | Make behavior/algorithms interchangeable          |
| Typical reason         | Vendor API differs from your application interface | Different ranking or analysis approaches          |
| Example                | Wrap a market-data SDK                             | Choose keyword vs vector ranking                  |
| Selection              | Often chosen by integration/configuration          | Often chosen by configuration, request, or policy |
| Can one class do both? | Yes                                                | Yes                                               |

An adapter may also implement a strategy interface. For example, a `CohereRerankingAdapter` could adapt a vendor API while serving as one selectable reranking strategy.

The patterns describe different roles; they are not mutually exclusive.

# 4. Repository pattern

## 4.1 The problem it solves

Your application needs to save and retrieve reviews. Without a repository, the service might contain database-specific queries:

Python

Run

```
class ReviewService:
    async def get_review(self, review_id, session):
        result = await session.execute(
            select(ReviewModel).where(
                ReviewModel.id == review_id
            )
        )
        return result.scalar_one_or_none()
```

Now the application service knows SQLAlchemy, table models, query syntax, and session behavior.

A repository gives the application a domain-oriented interface for data access.

## 4.2 Define the repository port

Python

Run

```
from typing import Protocol


class ReviewRepository(Protocol):
    async def get_by_id(self, review_id: str):
        ...

    async def save(self, review):
        ...
```

The service uses that contract:

Python

Run

```
class ReviewService:
    def __init__(self, reviews: ReviewRepository):
        self.reviews = reviews

    async def get_review(self, review_id: str):
        review = await self.reviews.get_by_id(review_id)

        if review is None:
            raise ReviewNotFound(review_id)

        return review
```

Then an infrastructure adapter implements the repository:

Python

Run

```
class SqlAlchemyReviewRepository:
    def __init__(self, session):
        self.session = session

    async def get_by_id(self, review_id: str):
        return await self.session.get(
            ReviewModel,
            review_id,
        )

    async def save(self, review):
        self.session.add(review)
        await self.session.flush()
        return review
```

Now the service asks for a review; it does not need to know how the database finds it.

## 4.3 Repository vs database

A repository is not the database itself.

* PostgreSQL stores the data.

* SQLAlchemy communicates with PostgreSQL.

* The SQLAlchemy repository implements your application's data-access contract.

* The application service uses the repository.

The dependency chain is:

ReviewService

ReviewRepository (port)

SQLAlchemy Repository (adapter)

PostgreSQL

The port belongs to the application/domain boundary; the SQLAlchemy implementation belongs to infrastructure.

## 4.4 Why not just use repositories everywhere?

Because abstraction has a cost. A repository is especially useful when:

* Data access is complex or repeated.

* You need unit tests independent of a real database.

* You want to isolate ORM models from application logic.

* You have multiple storage implementations or clear persistence boundaries.

It can be unnecessary ceremony for a tiny application or a simple query that has no meaningful boundary.

Also, a repository should express meaningful data operations—such as `get_active_policy_version()`—rather than becoming a generic wrapper around every SQL statement.


# 5. Planner–Supervisor pattern

This pattern is about deciding what work needs to happen, assigning that work, and coordinating the result.

It is particularly useful when a task is too complex for one LLM call.

## 5.1 First understand the two roles

### Planner: decides what needs to be done

The planner takes the user's request and converts it into a structured plan.

For example, a user submits this document:

> “Our investment product delivered 18% annual returns with low risk and charges a 1.5% management fee.”

The planner might identify these tasks:

Python

Run

```
plan = [
    {
        "task": "verify_return_claim",
        "required_evidence": "Approved performance disclosures",
    },
    {
        "task": "verify_risk_claim",
        "required_evidence": "Risk classification and disclosures",
    },
    {
        "task": "verify_fee_claim",
        "required_evidence": "Current approved fee schedule",
    },
]
```

The planner answers:

“What work is necessary to complete this request?”

It does not necessarily perform every task itself.

### Supervisor: coordinates execution

The supervisor takes the plan and manages the workers.

It may decide:

* Which specialist should handle each task.

* Which tasks can run concurrently.

* Whether a task needs more evidence.

* Whether the result needs another evaluation.

* Whether to finish, retry, or request human review.

The supervisor answers:

“Who should do the work, in what order, and what happens next?”

The distinction is conceptual. In a small system, the planner and supervisor may be implemented as one component. In a larger system, they may be separate nodes or services.

## 5.2 Example: compliance review

User document

Investment marketing material

Planner

Create performance, risk and fee tasks

Supervisor dispatches tasks

Performance specialist

Risk specialist

Fee specialist

Supervisor aggregates results

Sends findings to evaluation and subsequent workflow stages

The specialists can run concurrently because their tasks are largely independent. But they should not all be allowed to do anything they want. The supervisor should enforce which tasks and tools are permitted.

## 5.3 A simplified implementation

Python

Run

```
from dataclasses import dataclass


@dataclass
class Task:
    name: str
    specialist: str


class Planner:
    def create_plan(self, document: str) -> list[Task]:
        # In production, an LLM could propose a plan.
        # Validate its output against an allowed task schema.
        return [
            Task("performance_check", "performance"),
            Task("risk_check", "risk"),
            Task("fee_check", "fees"),
        ]


class Supervisor:
    def __init__(self, specialists: dict):
        self.specialists = specialists

    async def execute(self, tasks: list[Task], document: str):
        results = {}

        for task in tasks:
            # Only registered specialists can be called.
            specialist = self.specialists[task.specialist]

            results[task.name] = await specialist.run(
                document
            )

        return results
```

This is a simplified sequential supervisor. A production implementation could use `asyncio.gather()` for independent tasks, as well as timeouts, concurrency limits, per-task retries, and explicit error handling.

### Important: planner does not mean “let the LLM control everything”

A safe production design constrains the plan:

* Allowed task types are predefined.

* The planner cannot invent arbitrary tools.

* The supervisor validates task arguments.

* The workflow has a maximum number of steps.

* Sensitive actions require authorization.

* Failure and timeout paths are explicit.

For a compliance platform, an LLM can propose that a fee check is needed, but deterministic application code should enforce access controls and required review steps.

## 5.4 Planner–Supervisor vs a simple chain

A simple chain has a fixed path:

```
Retrieve → Analyze → Summarize
```

A planner–supervisor workflow can adapt within controlled limits:

```
Plan → Dispatch → Inspect results
                   ├── Missing evidence → Retrieve more
                   ├── Incomplete result → Retry/rework
                   └── Complete → Continue
```

Use a simple chain when the workflow is predictable. Use planning and supervision when the work varies by request, involves multiple specialists, or needs controlled branching.

In your compliance project, the planner/supervisor pattern is intended to coordinate specialist work, evaluation, and later workflow stages. Your investment project, by contrast, has a much smaller retrieval-and-analysis graph; its handoff labels alone do not make it a full planner–supervisor multi-agent system.

# 6. Evaluator / Rework loop

This is one of the most important concepts in production AI.

An LLM can produce an answer that sounds convincing but is incomplete, unsupported, or incorrect. The evaluator checks the output against defined requirements. If the output fails, the workflow can send it back for correction.

## 6.1 The basic flow

Specialist generates findings

Evaluator checks the result

Does it meet the requirements?

Yes

Finalize

No

Rework

Generate a corrected result

The rework loop should be bounded. Otherwise, an agent may repeatedly retry, consume tokens, and never finish.

## 6.2 What should the evaluator check?

For a financial compliance review, I would separate checks into several categories.

| Check              | Example                                                  |
| ------------------ | -------------------------------------------------------- |
| Schema validity    | Is the response valid JSON with all required fields?     |
| Completeness       | Were performance, risk and fee claims all assessed?      |
| Evidence grounding | Does each finding cite retrieved policy evidence?        |
| Citation validity  | Does the cited policy ID exist and apply to this review? |
| Semantic support   | Does the cited text actually support the finding?        |
| Policy consistency | Does the finding correctly apply the relevant policy?    |
| Risk handling      | Are high-risk findings routed for required human review? |

Some checks can be deterministic. Others may require a model-based evaluator, human review, or a combination.

For example, checking whether a citation ID exists is straightforward. Determining whether a policy passage actually supports a nuanced compliance conclusion is a harder semantic task.

## 6.3 A simple evaluator implementation

Python

Run

```
from dataclasses import dataclass


@dataclass
class Evaluation:
    passed: bool
    issues: list[str]


def evaluate(report: dict, allowed_policy_ids: set[str]):
    issues = []

    findings = report.get("findings")
    if not isinstance(findings, list):
        return Evaluation(False, ["findings must be a list"])

    for finding in findings:
        policy_id = finding.get("policy_id")

        if policy_id not in allowed_policy_ids:
            issues.append(
                f"Unknown policy ID: {policy_id}"
            )

        if not finding.get("rationale"):
            issues.append("Missing policy rationale")

        if not finding.get("evidence"):
            issues.append("Missing supporting evidence")

    return Evaluation(
        passed=len(issues) == 0,
        issues=issues,
    )
```

This evaluator checks structural and basic evidence requirements. It does not prove that the analysis is semantically correct.

That distinction matters in interviews. A schema validator is not a complete AI evaluator.

## 6.4 Add a bounded rework loop

Python

Run

```
MAX_REWORK_ATTEMPTS = 2


async def review_with_evaluation(document, policies):
    report = await generate_report(document, policies)

    for attempt in range(MAX_REWORK_ATTEMPTS + 1):
        evaluation = evaluate(
            report,
            allowed_policy_ids={p.id for p in policies},
        )

        if evaluation.passed:
            return report

        if attempt == MAX_REWORK_ATTEMPTS:
            break

        report = await revise_report(
            original_document=document,
            policies=policies,
            previous_report=report,
            issues=evaluation.issues,
        )

    # Do not silently accept a result that failed evaluation.
    raise ReviewNeedsHumanIntervention(
        "The report did not pass evaluation."
    )
```

This illustrates the control flow. In a production system, you would persist each attempt, record evaluator findings, apply time/token budgets, and route unresolved cases to human review.

## 6.5 What makes a good rework loop?

A robust loop needs:

1. A meaningful evaluator — not just “does the output look good?”

2. Actionable feedback — specify which finding or citation failed.

3. A targeted revision — correct the failed portion rather than regenerating everything unnecessarily.

4. A maximum retry count — prevent infinite loops.

5. A termination policy — pass, fail, or escalate.

6. Observability — record attempts, latency, token usage, and failure reasons.

7. Durable state — if the process crashes, recover the review without losing its progress.

Your compliance project's evaluator/rework design includes an evaluation stage and bounded rework. But the important implementation distinction is that completeness and known-policy-ID checks do not, by themselves, establish semantic correctness.

# 7. How these concepts work together in one request

Let's connect everything into a single end-to-end example.

A user submits a financial marketing document claiming “18% annual returns with low risk and a 1.5% fee.”

1. FastAPI receives the request

   An inbound adapter validates the request and calls the application use case.

2. Repository loads and saves data

   The application loads the review, policy versions, and relevant metadata through repository interfaces.

3. Planner creates tasks

   It identifies the performance, risk, and fee claims that need checking.

4. Supervisor coordinates specialists

   It dispatches approved tasks and collects their results.

5. Adapters connect external systems

   LLM, vector database, market-data, and other provider adapters translate application-level requests into external API operations.

6. Evaluator checks the report

   It verifies structure, evidence, citations, and the required quality criteria.

7. Rework or escalate

   Failed checks trigger bounded revision. Unresolved or high-risk cases go to human review when required.

8. Repository persists the outcome

   The application stores findings, review status, evidence references, and audit information before returning the appropriate response.

The architecture separates two concerns:

* Software architecture: ports, adapters, repositories, dependency direction.

* AI workflow: planning, supervision, specialist execution, evaluation, and rework.

You need both. A well-designed AI workflow can still be tightly coupled to its database and provider SDKs. Conversely, a beautifully layered application can still produce poor results if its evaluator is weak.

# 8. Common interview questions and senior-level answers

1. Is a repository the same as an adapter?

No. Repository describes a data-access role and usually exposes domain-oriented persistence operations. Adapter is a broader pattern for translating between an application's port and an external interface. A SQLAlchemy repository is often an adapter that implements a repository port.

2. Is Strategy the same as dependency injection?

3. Is a planner always an LLM?

4. Can the evaluator be another LLM?

5. What prevents an evaluator loop from running forever?

6. Why use hexagonal architecture in an AI application?

## The final mental model

* Hexagonal architecture protects the core from infrastructure changes.

* Ports define what the core needs.

* Adapters connect those ports to concrete technologies.

* Strategy lets you select different behaviors behind a common contract.

* Repository gives application code a clean way to load and persist data.

* Planner decides what tasks are needed.

* Supervisor coordinates their execution.

* Evaluator checks whether the result meets defined requirements.

* Rework loop attempts bounded correction before completion or escalation.

For a senior/staff engineer interview, the most important point is not just defining each pattern. Explain which problem it solves, where it belongs, how it interacts with the other patterns, and what failure modes you would guard against in production.
