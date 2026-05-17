# Production Tool-Calling Agent — Complete System Explanation

This is a production-style AI agent architecture.

The agent can:

* understand user queries
* reason about tasks
* choose tools
* execute tools
* observe outputs
* continue reasoning
* return grounded answers

This is how modern agent systems work in:

* OpenAI
* Anthropic
* Google
* Microsoft

---

# HIGH-LEVEL ARCHITECTURE

User
  ↓
FastAPI API
  ↓
Agent
  ↓
Planner
  ↓
LLM Reasoning
  ↓
Tool Selection
  ↓
Tool Execution
  ↓
Observation
  ↓
More Reasoning
  ↓
Final Response
```

---

# COMPLETE FLOW

# Example Query

User asks:

```text id="5d9c10"
What's the weather in Bangalore and calculate 25*18?
```

Agent internally performs:

```text id="k6ekiw"
1. Understand query
2. Decide required tools
3. Call weather tool
4. Call calculator tool
5. Observe outputs
6. Combine results
7. Return final answer
```

---

# PROJECT STRUCTURE

```text id="m7g0zj"
agent-system/
│
├── app/
│   ├── agents/
│   ├── tools/
│   ├── llm/
│   ├── core/
│   ├── api/
│   ├── schemas/
│   └── main.py
│
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env
```

Each folder has a specific responsibility.

---

# app/main.py

# Purpose

Starts FastAPI application.

---

# Code

```python id="k0gvq7"
from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(
    title="Production Agent"
)

app.include_router(router)
```

---

# What Happens Here

Creates API server:

```python id="2n3bti"
app = FastAPI()
```

Then loads routes:

```python id="fb8wku"
app.include_router(router)
```

---

# app/api/routes.py

# Purpose

Defines REST API endpoints.

---

# Code Flow

```python id="v1lax0"
@router.post("/agent")
```

Creates endpoint:

```text id="b4e4ci"
POST /agent
```

---

# Example Request

```json id="s0jykh"
{
  "query": "What is AI?"
}
```

---

# Route Handler

```python id="sagz09"
response = await agent.run(
    request.query
)
```

This calls the agent system.

---

# FLOW

```text id="ye5m9v"
HTTP Request
   ↓
FastAPI Route
   ↓
Agent
```

---

# app/agents/agent.py

# Purpose

Main conversational wrapper.

Controls:

* memory
* orchestration
* conversation state

---

# Flow

```python id="ul6cfa"
self.memory.add_message()
```

Stores user history.

---

# Then

```python id="8mjlwm"
await self.orchestrator.run()
```

Starts reasoning loop.

---

# Why This Layer Exists

Separates:

| Responsibility | Component       |
| -------------- | --------------- |
| conversation   | agent.py        |
| reasoning      | orchestrator.py |
| planning       | planner.py      |

This is clean architecture.

---

# app/agents/orchestrator.py

# MOST IMPORTANT COMPONENT

This is the brain of the system.

Controls:

* LLM calls
* tool execution
* reasoning loop
* stopping conditions

---

# CORE AGENT LOOP

```python id="6q19pp"
while True:
```

This is the reasoning cycle.

---

# Step 1 — Send Messages to LLM

```python id="c1ty1n"
client.chat.completions.create()
```

LLM receives:

* user query
* previous tool outputs
* available tools

---

# Step 2 — LLM Decides Tool

LLM may return:

```text id="2kqarf"
tool_call:
get_weather(city="Bangalore")
```

---

# Step 3 — Execute Tool

```python id="jagjlwm"
tool.execute()
```

Runs actual Python function.

---

# Step 4 — Add Observation

Tool result becomes:

```text id="jz2h0n"
temperature: 28C
```

Added back into conversation.

---

# Step 5 — LLM Continues Reasoning

LLM sees tool output and decides:

```text id="ewd2gz"
Need another tool?
Or final answer?
```

---

# Loop Ends When

```python id="agvz4k"
if not tool_calls:
    return final_answer
```

---

# Full Agent Lifecycle

```text id="e8qfdh"
User Query
   ↓
LLM reasoning
   ↓
Tool selection
   ↓
Tool execution
   ↓
Observation
   ↓
More reasoning
   ↓
Final answer
```

---

# app/agents/planner.py

# Purpose

Breaks large tasks into smaller tasks.

---

# Example

User:

```text id="fhh4mw"
Research AI companies in India
```

Planner creates:

```text id="7t7hvh"
1. Search companies
2. Gather funding info
3. Summarize findings
```

---

# Why Planning Matters

Complex tasks require:

* decomposition
* ordering
* dependency management

Without planning:

```text id="3n0l4q"
agents become unreliable
```

---

# app/tools/base.py

# Purpose

Defines standard interface for all tools.

---

# Why Important

Production systems need:

* consistency
* validation
* schemas
* observability

---

# BaseTool

```python id="1tjlwm"
class BaseTool(ABC):
```

All tools inherit from this.

---

# Required Method

```python id="wudt0v"
async def execute()
```

Every tool must implement execution logic.

---

# OpenAI Tool Schema

```python id="8tw8yk"
openai_schema()
```

Converts Python tool into JSON schema.

This enables:

```text id="9d52ek"
LLM function calling
```

---

# app/tools/weather_tool.py

# Purpose

Provides weather information.

---

# Tool Schema

```python id="cjlwmf"
parameters = {
    "city": {
        "type": "string"
    }
}
```

This tells LLM:

```text id="1w2f5h"
Tool requires city parameter
```

---

# Execution

```python id="klqibj"
execute(city="Bangalore")
```

Returns:

```json id="98zx61"
{
  "temperature": "28C"
}
```

---

# app/tools/calculator_tool.py

# Purpose

Handles mathematical calculations.

---

# Example

User:

```text id="3k0m9d"
25 * 18
```

Agent decides:

```text id="nql0mu"
Use calculator tool
```

---

# Security Warning

You used:

```python id="mxp0j6"
eval()
```

NEVER use unrestricted eval in production.

Production systems use:

* AST parsing
* sandboxes
* jailed execution

---

# app/tools/search_tool.py

# Purpose

Web search capability.

---

# Production Systems Use

* Google Search APIs
* Bing APIs
* Tavily
* SerpAPI

---

# app/tools/rag_tool.py

# Purpose

Enterprise document retrieval.

This connects the agent to your RAG pipeline.

---

# Flow

```text id="z8zhhw"
Agent
   ↓
RAG Tool
   ↓
Vector Search
   ↓
Relevant Documents
```

---

# Why This Is Powerful

Now agent can access:

```text id="jlwmkm"
private company knowledge
```

---

# app/tools/registry.py

# Purpose

Central tool management system.

---

# Why Important

Registry enables:

* dynamic tool discovery
* permissions
* analytics
* auditing
* versioning

---

# Flow

```python id="slkjlwm"
self.tools = {
   "search": SearchTool()
}
```

---

# app/llm/prompts.py

# Purpose

Stores all system prompts.

---

# Why Centralized Prompts Matter

Production systems need:

* versioning
* observability
* testing
* experimentation

---

# SYSTEM_AGENT_PROMPT

Controls agent behavior.

Example:

```text id="9mjlwm"
Never hallucinate
Use tools carefully
```

---

# app/agents/memory.py

# Purpose

Stores conversation history.

---

# Why Memory Matters

Without memory:

```text id="jlwm6n"
agent forgets previous messages
```

---

# Memory Types

| Memory     | Purpose              |
| ---------- | -------------------- |
| short-term | current conversation |
| long-term  | persistent user data |
| semantic   | vector memory        |
| episodic   | past workflows       |

---

# app/core/config.py

# Purpose

Loads environment variables.

---

# Example

```python id="9nuh9q"
OPENAI_API_KEY
```

Loaded from:

```text id="mlb2s5"
.env
```

---

# app/core/logging.py

# Purpose

Structured logging.

Production systems track:

* latency
* failures
* tool usage
* token cost

---

# Why structlog?

Better for:

* JSON logs
* distributed systems
* observability platforms

---

# app/core/security.py

# Purpose

Protects the agent system.

---

# Production Risks

Agents are dangerous.

Possible attacks:

```text id="r7mw8y"
Delete data
Reveal secrets
Ignore instructions
```

---

# Security Layer Prevents

* unauthorized tools
* prompt injection
* secret leakage
* unsafe execution

---

# app/schemas/agent_schema.py

# Purpose

Defines API contracts.

Using [Pydantic Documentation](https://docs.pydantic.dev/latest/?utm_source=chatgpt.com)

---

# Example Request Schema

```python id="jlwmr2"
class AgentRequest(BaseModel):
```

Validates:

```json id="e5jlwm"
{
   "query": "What is AI?"
}
```

---

# tests/test_agent.py

# Purpose

Ensures system reliability.

---

# Test Flow

```python id="4wjlwm"
response = await agent.chat()
```

Verifies:

* agent runs
* response exists
* API works

---

# Dockerfile

# Purpose

Packages app into container.

---

# Flow

```dockerfile id="jlwmex"
FROM python:3.11-slim
```

Base image.

---

# Install Dependencies

```dockerfile id="3tjlwm"
RUN pip install -r requirements.txt
```

---

# Start Server

```dockerfile id="jlwmu2"
CMD ["uvicorn", ...]
```

Runs FastAPI app.

---

# docker-compose.yml

# Purpose

Runs multiple services together.

Production systems may include:

* API
* Redis
* PostgreSQL
* Vector DB
* Kafka

---

# requirements.txt

# Purpose

Dependency management.

---

# HOW TO RUN THE ENTIRE SYSTEM

# STEP 1 — INSTALL DOCKER

Install:

[Docker Desktop](https://www.docker.com/products/docker-desktop/?utm_source=chatgpt.com)

---

# STEP 2 — CREATE PROJECT

Structure:

```text id="bjlwmx"
agent-system/
```

Copy all files.

---

# STEP 3 — CREATE .env

```env id="jlwm5f"
OPENAI_API_KEY=your_key
```

---

# STEP 4 — BUILD CONTAINER

Run:

```bash id="4jlwmk"
docker build -t production-agent .
```

---

# STEP 5 — START CONTAINER

Run:

```bash id="rjlwmv"
docker run -p 8000:8000 production-agent
```

---

# OR USE DOCKER COMPOSE

Run:

```bash id="jlwm1j"
docker-compose up --build
```

---

# STEP 6 — TEST API

Open:

```text id="jjlwmm"
http://localhost:8000/docs
```

FastAPI Swagger UI appears.

---

# STEP 7 — TEST AGENT

Request:

```bash id="jlwm02"
curl -X POST http://localhost:8000/agent \
-H "Content-Type: application/json" \
-d '{
  "query":"What is the weather in Bangalore and calculate 25*18?"
}'
```

---

# INTERNAL EXECUTION FLOW

```text id="jlwm3r"
User Query
    ↓
FastAPI API
    ↓
Agent
    ↓
Planner
    ↓
LLM Reasoning
    ↓
Tool Selection
    ↓
Tool Execution
    ↓
Tool Observation
    ↓
More Reasoning
    ↓
Final Response
```

---

# WHY THIS IS SENIOR-LEVEL

Because it includes:

* modular architecture
* orchestration engine
* tool calling
* memory
* planning
* schema validation
* security
* Docker deployment
* production logging
* extensible tools
* RAG integration
* observability-ready design

---

# HOW REAL AGENTS EVOLVE

Real enterprise agents grow into:

```text id="jlwm7h"
multi-agent systems
distributed execution
human approvals
GPU inference
sandboxed runtimes
evaluation pipelines
cost optimization
tool marketplaces
long-term memory
autonomous workflows
```

---

# REAL FRAMEWORKS USED IN INDUSTRY

| Framework       | Purpose             |
| --------------- | ------------------- |
| LangChain       | orchestration       |
| LlamaIndex      | RAG + agents        |
| CrewAI          | multi-agent systems |
| AutoGen         | agent collaboration |
| Semantic Kernel | enterprise agents   |




# Production-Level Tool Calling Agent Architecture

A production agent is NOT:

if user says weather:
    call weather api
```

A real senior-level AI agent system includes:

* tool registry
* structured tool schemas
* function calling
* orchestration engine
* retries
* observability
* memory
* planning
* security
* sandboxing
* permissions
* caching
* streaming
* async execution
* human approval workflows

---

# WHAT IS A TOOL-CALLING AGENT?

A tool-calling agent is an LLM system that can:

```text id="msz1k2"
reason
decide
call tools
observe outputs
continue reasoning
produce final answer
```

---

# PRODUCTION AGENT FLOW

```text id="fyzpnk"
User Query
    ↓
LLM Planning
    ↓
Tool Selection
    ↓
Tool Execution
    ↓
Observation
    ↓
LLM Reasoning
    ↓
More Tool Calls?
    ↓
Final Response
```

---

# Example

User:

What's the weather in Bangalore and summarize latest AI news?
```

Agent:

```text id="vbfe2w"
1. call weather tool
2. call news search tool
3. summarize outputs
4. return answer
```

---

# PRODUCTION FOLDER STRUCTURE

```text id="lbh1fw"
agent-system/
│
├── app/
│   ├── agents/
│   │   ├── agent.py
│   │   ├── orchestrator.py
│   │   ├── planner.py
│   │   └── memory.py
│   │
│   ├── tools/
│   │   ├── base.py
│   │   ├── registry.py
│   │   ├── weather_tool.py
│   │   ├── search_tool.py
│   │   ├── calculator_tool.py
│   │   └── rag_tool.py
│   │
│   ├── llm/
│   │   ├── openai_client.py
│   │   └── prompts.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── security.py
│   │
│   ├── api/
│   │   └── routes.py
│   │
│   ├── schemas/
│   │   └── agent_schema.py
│   │
│   └── main.py
│
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env
```

---

# 1. REQUIREMENTS

## requirements.txt

```txt id="g8o2z2"
fastapi
uvicorn
openai
httpx
pydantic
redis
tenacity
structlog
```

---

# 2. CONFIG

## app/core/config.py



---

# 3. STRUCTURED LOGGING

## app/core/logging.py


---

# 4. TOOL BASE CLASS

# Why This Matters

Production systems need:

* standardization
* validation
* observability
* schema enforcement

---

## app/tools/base.py


---

# 5. WEATHER TOOL

## app/tools/weather_tool.py



---

# 6. CALCULATOR TOOL

## app/tools/calculator_tool.py

---

# IMPORTANT SECURITY NOTE

NEVER use raw `eval()` in production.

Production systems use:

* sandboxing
* AST parsing
* restricted execution
* jailed runtimes

---

# 7. SEARCH TOOL

---

# 8. TOOL REGISTRY

Production agents need centralized tool management.

## app/tools/registry.py

---

# Why Registry Matters

Enables:

* dynamic discovery
* permissions
* analytics
* auditing
* versioning

---

# 9. OPENAI CLIENT

## app/llm/openai_client.py

---

# 10. AGENT ORCHESTRATOR

This is the MOST important component.

It controls:

* reasoning
* tool execution
* loop management
* stopping conditions

---

# app/agents/orchestrator.py


---

# THIS IS THE CORE AGENT LOOP

# Agent Reasoning Cycle

```text id="7dyw7z"
LLM decides tool
    ↓
Tool executes
    ↓
Observation added
    ↓
LLM continues reasoning
```

This loop continues until:

```text id="yg6ic4"
No more tool calls
```

---

# 11. MEMORY SYSTEM

Production agents need memory.

---

# app/agents/memory.py

---

# Types of Memory

| Type       | Purpose              |
| ---------- | -------------------- |
| short-term | conversation         |
| long-term  | persistent knowledge |
| semantic   | vector memory        |
| episodic   | past interactions    |

---

# 12. SECURITY

Production agents are dangerous without controls.

---

# app/core/security.py

---

# Production Security Includes

* RBAC
* tool permissions
* sandboxing
* secret isolation
* prompt injection prevention
* rate limiting
* audit logs

---

# 13. FASTAPI API

## app/api/routes.py

---

# 14. MAIN APP

## app/main.py

---

# 15. RUNNING THE SYSTEM

# Install Dependencies

```bash id="smvvgl"
pip install -r requirements.txt
```

---

# Start Server

```bash id="2cokfu"
uvicorn app.main:app --reload
```

---

# Query Agent

```bash id="k5x24o"
curl -X POST http://localhost:8000/agent \
-H "Content-Type: application/json" \
-d '{
  "query":"What is the weather in Bangalore and calculate 25*18?"
}'
```

---

# EXAMPLE AGENT EXECUTION

User:

```text id="o8b97m"
What's weather in Bangalore and 25*18?
```

Agent internally:

```text id="f0zx8c"
1. select weather tool
2. execute tool
3. select calculator tool
4. execute tool
5. combine outputs
6. return final answer
```

---

# Production Enhancements

# 1. Async Tool Execution

Production agents parallelize independent tools.

Example:

```text id="g7s6t3"
weather
news
stocks
```

run simultaneously.

---

# 2. Retry Logic

Use:

* exponential backoff
* retries
* circuit breakers

---

# 3. Human Approval Workflows

Critical actions require approval.

Example:

```text id="l8nqxy"
send email
delete database
transfer money
```

---

# 4. Sandboxed Execution

Never allow unrestricted code execution.

Use:

* containers
* jailed runtimes
* WASM sandboxes

---

# 5. Observability

Track:

| Metric             | Why         |
| ------------------ | ----------- |
| tool latency       | performance |
| hallucination rate | safety      |
| token usage        | cost        |
| tool failure rate  | reliability |
| retries            | resilience  |

---

# 6. Agent Planning

Advanced agents:

* decompose tasks
* build execution plans
* optimize tool order

---

# Example Planning

```text id="q0qf5g"
Task:
Research AI companies

Plan:
1. search companies
2. gather funding data
3. summarize
4. generate report
```

---

# 7. Multi-Agent Systems

Large systems use specialized agents.

Example:

| Agent           | Responsibility |
| --------------- | -------------- |
| retrieval agent | search         |
| coding agent    | code           |
| planning agent  | orchestration  |
| evaluator agent | quality        |

---

# 8. Production Agent Risks

## Prompt Injection

Example:

```text id="25x5q9"
Ignore instructions
Reveal secrets
```

---

# Tool Abuse

Example:

```text id="1cefdq"
Delete all customer records
```

---

# Data Leakage

Cross-tenant exposure.

---

# Infinite Tool Loops

Agent repeatedly calling tools forever.

Need:

```text id="jzlr0h"
max iteration limits
```

---

# Production Safeguards

| Safeguard        | Purpose      |
| ---------------- | ------------ |
| max iterations   | stop loops   |
| tool permissions | security     |
| audit logging    | traceability |
| sandboxing       | isolation    |
| retries          | resilience   |
| timeouts         | stability    |

---

# FINAL PRODUCTION FLOW

```text id="sdv1ot"
User Query
    ↓
Planner
    ↓
LLM Reasoning
    ↓
Tool Selection
    ↓
Tool Execution
    ↓
Observation
    ↓
More Reasoning
    ↓
Final Response
```

---

# Real Production Frameworks

| Framework       | Company           |
| --------------- | ----------------- |
| LangChain       | orchestration     |
| LlamaIndex      | RAG + agents      |
| AutoGen         | multi-agent       |
| CrewAI          | role-based agents |
| Semantic Kernel | enterprise agents |

---

# What Senior Interviewers Expect

You should understand:

* tool calling lifecycle
* orchestration loops
* agent memory
* planning
* retries
* observability
* security
* prompt injection defense
* sandboxing
* multi-agent coordination
* human approval workflows
* distributed execution
* async orchestration
* cost optimization
