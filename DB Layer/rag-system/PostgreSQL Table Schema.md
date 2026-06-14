-- =========================
-- 🧑 Users Table (optional)
-- =========================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- 💬 Chat History Table
-- =========================
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast retrieval
CREATE INDEX idx_chat_user_id ON chat_history(user_id);


-- =========================
-- 📊 Document Metadata Table (optional for ingestion tracking)
-- =========================
CREATE TABLE documents (
    id VARCHAR(255) PRIMARY KEY,
    title TEXT,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);




You don’t “run it inside Python” — you run the **PostgreSQL table schema (DDL SQL)** inside a **PostgreSQL database environment**.

Here are the exact ways you can execute it 👇

---

# 🐘 1. Run using `psql` (Terminal way — most common in production)

### Step 1: Connect to PostgreSQL

```bash
psql -U postgres -h localhost -d ragdb
```

If DB doesn’t exist:

```bash
createdb ragdb
```

---

### Step 2: Paste SQL directly

Once inside `psql`, paste:

```sql
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

# 🧑‍💻 2. Run using PgAdmin (GUI method — easiest for beginners)

### Steps:

1. Open **PgAdmin**
2. Connect to your PostgreSQL server
3. Select your database (`ragdb`)
4. Open:

   ```
   Tools → Query Tool
   ```
5. Paste SQL schema
6. Click ▶️ Run

---

# 🐳 3. Run using Docker PostgreSQL (Recommended for AI projects)

If you are building RAG systems (like production setups):

### Start PostgreSQL container:

```bash
docker run -d \
  --name postgres-db \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=admin \
  -e POSTGRES_DB=ragdb \
  -p 5432:5432 \
  postgres
```

### Then connect:

```bash
psql -U admin -h localhost -d ragdb
```

Run your schema there.

---

# ⚡ 4. Run automatically using Python (production way)

You can also execute schema from code:

```python id="run_sql"
import psycopg2

conn = psycopg2.connect(
    dbname="ragdb",
    user="admin",
    password="admin",
    host="localhost",
    port="5432"
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

conn.commit()
conn.close()
```

---

# 🧠 Where this fits in your AI project

In a real RAG system:

```
FastAPI app
   ↓
PostgreSQL (chat_history table runs here)
   ↓
Used by rag_pipeline.py to store conversations
```

So this schema is **NOT part of runtime logic** — it is **database initialization step**.

---

# 🎯 Interview-ready answer

If interviewer asks:

### ❓ “Where do you run PostgreSQL schema?”

Say:

> “We execute PostgreSQL schema using either psql CLI, PgAdmin GUI, or automated migration tools like Alembic in production. In containerized environments, we often initialize schemas via Docker entrypoint scripts or migration pipelines during deployment.”

---

# 🚀 If you want next level (important for interviews):

I can show you:

* 🔥 Alembic migrations (production-grade DB versioning)
* 🔥 Docker Compose setup for Postgres + Redis + Qdrant
* 🔥 Full CI/CD DB initialization pipeline
* 🔥 Multi-tenant PostgreSQL design for SaaS AI apps

Just tell me 👍


For a **Senior AI Engineer interview**, simply creating a `chat_history` table is not enough. Most enterprise AI platforms are **multi-tenant SaaS systems**, meaning a single platform serves multiple companies (tenants) while keeping their data isolated.

Examples:

* [OpenAI Enterprise](https://openai.com/enterprise/?utm_source=chatgpt.com)
* [Anthropic Team & Enterprise](https://www.anthropic.com?utm_source=chatgpt.com)
* [Microsoft Copilot Studio](https://www.microsoft.com/copilot/microsoft-copilot-studio?utm_source=chatgpt.com)

All of them use some form of tenant isolation.

---

# Architecture

Suppose your SaaS AI platform serves:

| Tenant   | Users |
| -------- | ----- |
| EY       | 500   |
| Deloitte | 1000  |
| Infosys  | 5000  |

Each company should only see its own:

* Documents
* Chats
* Agents
* Knowledge Bases
* API Usage
* Billing

---

# Option 1 (Most Common): Shared Database + Tenant ID

This is the most widely used architecture.

## Tenants

```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    tenant_name VARCHAR(255) NOT NULL,
    plan VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Example:

| id | tenant_name |
| -- | ----------- |
| t1 | EY          |
| t2 | Deloitte    |

---

## Users

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Chat History

```sql
CREATE TABLE chat_history (
    id BIGSERIAL PRIMARY KEY,

    tenant_id UUID NOT NULL,
    user_id UUID NOT NULL,

    query TEXT NOT NULL,
    response TEXT NOT NULL,

    model_name VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Documents

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY,

    tenant_id UUID NOT NULL,

    filename VARCHAR(255),
    source_type VARCHAR(50),

    uploaded_by UUID,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

# Why Tenant ID Everywhere?

Every query becomes:

```sql
SELECT *
FROM chat_history
WHERE tenant_id = 'EY_TENANT_ID';
```

This prevents Deloitte from seeing EY data.

---

# Production Indexing

```sql
CREATE INDEX idx_chat_tenant
ON chat_history(tenant_id);

CREATE INDEX idx_chat_user
ON chat_history(user_id);

CREATE INDEX idx_chat_tenant_user
ON chat_history(tenant_id,user_id);
```

Interview point:

> We always index tenant_id because almost every query filters by tenant.

---

# Multi-Tenant Qdrant Design

A common mistake is putting everything into one collection without tenant separation.

Instead:

Payload example:

```python
{
    "tenant_id": "ey",
    "document_id": "doc_123",
    "chunk_id": "chunk_45",
    "text": "Revenue recognition policy..."
}
```

Search:

```python
client.search(
    collection_name="documents",
    query_vector=query_embedding,
    query_filter={
        "must": [
            {
                "key": "tenant_id",
                "match": {"value": "ey"}
            }
        ]
    }
)
```

This ensures EY retrieves only EY documents.

---

# Multi-Tenant Redis Design

Never do:

```python
chat:123
```

Instead:

```python
tenant:ey:user:123:chat
```

or

```python
tenant:deloitte:user:456:session
```

Example:

```python
redis.set(
    "tenant:ey:user:123:session",
    session_data
)
```

---

# AI Usage Tracking

Enterprise AI platforms usually track token consumption.

```sql
CREATE TABLE ai_usage (
    id BIGSERIAL PRIMARY KEY,

    tenant_id UUID NOT NULL,

    model_name VARCHAR(100),

    prompt_tokens INTEGER,
    completion_tokens INTEGER,

    total_cost NUMERIC(12,6),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Example:

| Tenant   | Cost  |
| -------- | ----- |
| EY       | $1200 |
| Deloitte | $5000 |

---

# Knowledge Base Design

```sql
CREATE TABLE knowledge_bases (
    id UUID PRIMARY KEY,

    tenant_id UUID NOT NULL,

    name VARCHAR(255),

    description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

# Agent Design

For multi-agent platforms:

```sql
CREATE TABLE agents (
    id UUID PRIMARY KEY,

    tenant_id UUID NOT NULL,

    name VARCHAR(255),

    model_name VARCHAR(100),

    system_prompt TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Example:

EY may have:

* Finance Agent
* Tax Agent
* Audit Agent

Deloitte may have:

* HR Agent
* Compliance Agent

---

# Enterprise-Level Security: PostgreSQL Row Level Security (RLS)

Many companies use PostgreSQL RLS.

```sql
ALTER TABLE chat_history
ENABLE ROW LEVEL SECURITY;
```

Policy:

```sql
CREATE POLICY tenant_policy
ON chat_history
USING (
    tenant_id =
    current_setting('app.tenant_id')::uuid
);
```

Application:

```python
cursor.execute(
    "SET app.tenant_id = %s",
    [tenant_id]
)
```

Now PostgreSQL automatically filters rows.

Interview point:

> We use PostgreSQL Row Level Security to enforce tenant isolation at the database layer rather than relying solely on application code.

---

# Production Architecture

```text
                    FastAPI
                       │
              JWT Tenant Context
                       │
      ┌────────────────┼────────────────┐
      │                │                │
      ▼                ▼                ▼

 PostgreSQL         Redis           Qdrant
 Structured      Session/Cache      Vectors

 tenant_id       tenant:user       tenant_id
 in every row    namespaced keys   payload filter

      │                │                │
      └────────────────┼────────────────┘
                       │
                    LLM Layer
            GPT / Claude / Llama
```

### Interview Answer

> In a multi-tenant AI SaaS platform, every business entity contains a tenant_id. PostgreSQL stores structured tenant data such as users, conversations, agents, and usage metrics. Qdrant stores embeddings with tenant-based payload filtering to ensure retrieval isolation. Redis namespaces keys using tenant identifiers for cache and session separation. For enterprise-grade security, we implement PostgreSQL Row Level Security (RLS) so tenant isolation is enforced directly by the database. This architecture allows a single deployment to securely serve multiple organizations while maintaining strict data segregation.
