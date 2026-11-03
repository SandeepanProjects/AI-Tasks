# Local API walkthrough

After `docker compose up --build`, create a local development token:

```bash
TOKEN=$(python scripts/create_dev_token.py)
```

The local token script uses the `.env` settings and grants demo-tenant analyst, reviewer and admin roles. It is strictly for local development.

## 1. Ingest tenant evidence

```bash
curl -X POST http://localhost:8000/v1/evidence/ingest \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "source_name": "demo-market-note",
    "source_uri": "fixture://demo/market-note-001",
    "content": "BTC Bitcoin digital asset market note. Digital assets can be volatile. Liquidity conditions, macroeconomic conditions and market structure can affect prices. This note is illustrative only and is not licensed market data.",
    "metadata": {"source_type": "demo", "licensed": false}
  }'
```

The API chunks the text, calculates content hashes, creates embeddings and inserts only unseen `(tenant_id, content_hash)` chunks. The hash includes source URI plus chunk text so identical text from different sources retains separate provenance.

## 2. Create a research review

```bash
curl -X POST http://localhost:8000/v1/reviews \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Idempotency-Key: btc-risk-review-0001' \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "Summarize BTC risk factors in the supplied evidence",
    "scope": {"assets": ["BTC"], "lookback_days": 30},
    "purpose": "risk_review"
  }'
```

The API writes the review, idempotency record, audit event and outbox event in one PostgreSQL transaction, then returns `202 Accepted`.

## 3. Poll the review

```bash
curl http://localhost:8000/v1/reviews/<review-id> \
  -H "Authorization: Bearer $TOKEN"
```

The report is available to reviewer/admin roles while pending and to analysts only after approval.

## 4. Approve or reject

```bash
curl -X POST http://localhost:8000/v1/reviews/<review-id>/decision \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"decision": "approve", "comment": "Evidence reviewed."}'
```

A rejection or change request requires a reviewer comment of at least five characters.

## 5. Retry a failed review

Only an administrator can retry a terminal failure:

```bash
curl -X POST http://localhost:8000/v1/reviews/<review-id>/retry \
  -H "Authorization: Bearer $TOKEN"
```

The retry operation writes a new outbox event and audit event atomically.
