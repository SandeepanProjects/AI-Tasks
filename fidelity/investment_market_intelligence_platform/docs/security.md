# Security and compliance controls

## Identity and authorization
- JWT claims include `sub`, `tenant_id`, and `roles`. In production use OIDC/JWKS and key rotation.
- Tenant is server-derived; never accept it from client body.
- Reviewer decisions require `reviewer` or `admin`; use separation of duties for production.
- PostgreSQL RLS is defense in depth. Apply `app.tenant_id` transaction-locally and ensure application DB role cannot bypass RLS.

## LLM threat model
- Prompt injection can appear in scraped pages, filings, analyst notes, or user prompts.
- Treat retrieved content as data, not instructions. Do not expose secrets or tools to the model.
- Tools are typed and allow-listed. No arbitrary URL, SQL, shell, order placement, or wallet signing.
- Validate structured outputs and every cited evidence ID against the retrieval result set.
- Limit context size, request size, output tokens, tool calls, recursion, and wall-clock time.
- Redact credentials and sensitive personal data before model calls; maintain vendor data-processing approvals.

## Scraping and market-data governance
- Only use sources whose terms/license permit collection and analysis.
- Enforce host allow-lists, DNS/IP checks against SSRF, redirect restrictions, MIME/size limits, rate limits, and crawl budgets.
- Record provider, timestamp, currency, adjustment methodology, and delayed/live status.
- Never infer live prices from stale or fixture data.
- Sentiment is noisy and may be manipulated; label methodology and confidence.

## Operational security
- TLS in transit, encryption at rest, secret manager, least-privilege IAM, network segmentation.
- Immutable audit trail for approvals, prompt/model version, evidence IDs, tool calls, and output hash.
- Retention, deletion, legal hold, access reviews, incident response, backup/PITR, disaster recovery.
