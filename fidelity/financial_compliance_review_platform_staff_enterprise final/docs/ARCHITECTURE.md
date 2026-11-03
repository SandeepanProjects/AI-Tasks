# Architecture

```text
API → PostgreSQL review/audit → Celery/Redis → Worker
                                            ↓
                              LangGraph + PostgreSQL checkpointer
                                ├─ tenant-filtered policy retrieval
                                ├─ pgvector embeddings + keyword fallback
                                ├─ parallel specialist LLM agents
                                ├─ semantic completeness/evidence checks
                                └─ interrupt() → reviewer → Command(resume)
```

Celery messages carry primitive IDs and decision data, not ORM objects. Each review uses a stable graph thread ID. All policy retrieval is tenant scoped. The graph is compiled with a PostgreSQL checkpointer in the worker lifecycle.
