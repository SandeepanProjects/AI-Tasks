In our Financial Compliance Review Platform, PostgreSQL is the primary relational database and acts as the system of record.

We store the application's business data, review information, compliance findings, and audit history in PostgreSQL.

Let's break it down with examples.

## 1. What exactly do we store in PostgreSQL?

| Table                 | What we store                                                      |
| --------------------- | ------------------------------------------------------------------ |
| `users`               | User ID, name, email, role                                         |
| `tenants`             | Financial institution or organization details                      |
| `documents`           | Uploaded document name, type, storage path, upload date, tenant ID |
| `reviews`             | Review ID, document ID, status, submitted_by, created_at           |
| `compliance_policies` | Policy ID, policy name, policy content, version, effective date    |
| `policy_chunks`       | Chunk text, policy ID, page number, metadata, embedding vector     |
| `compliance_findings` | Identified violation, risk level, explanation, policy reference    |
| `review_approvals`    | Approver ID, approval status, comments, decision date              |
| `audit_logs`          | User actions, review changes, timestamps                           |

## 2. Example of an actual review

Suppose an advisor uploads a financial marketing document containing:

"Investors are guaranteed 15% annual returns."

Our platform processes it.

Step 1: Document information

In the `documents` table:

```
{
  "document_id": "DOC101",
  "filename": "investment_proposal.pdf",
  "tenant_id": "BANK01",
  "uploaded_by": "USER101"
}
```

Step 2: Review information

In the `reviews` table:

```
{
  "review_id": "REV101",
  "document_id": "DOC101",
  "status": "COMPLETED",
  "submitted_by": "USER101"
}
```

Step 3: Compliance findings

In the `compliance_findings` table:

```
{
  "finding_id": "F101",
  "review_id": "REV101",
  "claim": "Guaranteed 15% annual returns",
  "policy_id": "POL101",
  "violation": true,
  "risk_level": "HIGH",
  "explanation": "Investment returns cannot be guaranteed."
}
```

Step 4: Human approval

In the `review_approvals` table:

```
{
  "review_id": "REV101",
  "approver_id": "USER202",
  "decision": "REJECTED",
  "comments": "Remove guaranteed return statement."
}
```

## 3. What about embeddings? Are they also stored in PostgreSQL?

Yes. We use the `pgvector` extension.

For example, when we ingest compliance policies:

```
Compliance Policy
       |
       v
Text Chunking
       |
       v
Embedding Model
       |
       v
Vector Embeddings
       |
       v
PostgreSQL + pgvector
```

A policy chunk might look like:

| chunk_id | policy_id | content                                 | embedding         |
| -------- | --------- | --------------------------------------- | ----------------- |
| C101     | POL101    | Investment returns cannot be guaranteed | [0.12, 0.45, ...] |
| C102     | POL102    | Risks must be disclosed                 | [0.32, 0.21, ...] |

When a user submits a document, we generate an embedding for its claim and search these stored policy embeddings for relevant evidence.

## 4. What is stored in Redis versus PostgreSQL?

This is a common interview question.

| PostgreSQL          | Redis                                          |
| ------------------- | ---------------------------------------------- |
| User records        | Temporary cache                                |
| Document metadata   | Celery task broker                             |
| Review records      | Frequently accessed policy results             |
| Compliance findings | Temporary workflow-related data, if configured |
| Policy metadata     | Short-lived cached responses                   |
| Approval history    | Task coordination                              |

PostgreSQL provides durable business-data storage. Redis primarily supports caching and asynchronous task coordination.

## 5. Interview-ready answer

If the interviewer asks, "What exactly did you store in PostgreSQL?", answer:

"We used PostgreSQL as our primary relational database and system of record. We stored user information, tenant details, document metadata, review requests, compliance policies, identified violations, risk classifications, human approval decisions, and audit logs.

We also integrated pgvector with PostgreSQL to store policy embeddings and perform semantic similarity searches for our RAG pipeline.

So PostgreSQL served two purposes: transactional business-data persistence and vector-based policy retrieval."

Remember this distinction: We generally store the actual uploaded PDF in object storage such as S3, not directly in PostgreSQL. PostgreSQL stores its metadata and storage reference.