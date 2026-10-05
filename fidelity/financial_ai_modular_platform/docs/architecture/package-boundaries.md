# Package boundaries

| Concern | Shared package | Application |
|---|---|---|
| JWT parsing | platform-auth | |
| Generic RBAC engine | platform-auth | |
| Compliance permission | | financial-compliance |
| Async SQLAlchemy session | platform-db | |
| Compliance repository | | financial-compliance |
| Redis client | platform-cache | |
| Compliance cache keys | | financial-compliance |
| LLM abstraction | ai-llm | |
| Compliance prompts | | financial-compliance |
| Chunking/retrieval contracts | ai-rag | |
| Policy relevance rules | | financial-compliance |
| Generic agent runtime | ai-agents | |
| Compliance Research Agent | | financial-compliance |
| Generic evaluator contract | ai-agents | |
| Compliance evaluator rules | | financial-compliance |
| Prompt-injection detector | ai-guardrails | |
| Financial marketing policy | | financial-compliance |
| Logging/tracing primitives | platform-observability | |
