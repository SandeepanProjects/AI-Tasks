# AWS implementation guide

This repository keeps the local Docker stack and adds optional AWS adapters. AWS credentials are not required to import or run the local profile. In AWS, attach an ECS task role; do not put access keys in `.env` or container images.

## Implemented AWS integrations

| Capability | Implementation | Runtime configuration |
|---|---|---|
| Original policy document storage | `app/aws/storage.py` using S3, tenant-prefixed object keys, SSE-S3 or SSE-KMS | `AWS_S3_BUCKET`, `AWS_S3_PREFIX`, `AWS_KMS_KEY_ID` |
| Scanned multi-page PDF OCR | `app/aws/textract.py` using asynchronous Textract jobs against the uploaded S3 object | AWS region and Textract polling settings |
| Embeddings | `app/aws/bedrock_embeddings.py` using Bedrock Runtime | `EMBEDDING_PROVIDER=bedrock` |
| Agent LLM | `app/aws/bedrock_chat.py` using LangChain AWS Converse integration | `LLM_PROVIDER=bedrock` |
| API document upload | `POST /v1/documents/upload` stores the original in S3, extracts text and indexes policy chunks | `AWS_S3_BUCKET` required |
| AWS foundation | Terraform S3 bucket, versioning, public-access block, TLS-only bucket policy, customer-managed KMS key, ECS task/execution IAM roles | `infra/terraform/` |

The Bedrock embedding adapter defaults to `amazon.titan-embed-text-v1` because it returns 1536 dimensions, matching the current `vector(1536)` database column. If you switch to Titan v2, Cohere or another model with a different vector size, create a migration and re-embed the entire corpus before changing the configured model. Do not mix vector dimensions in one index.

## Install and configure

```bash
pip install -e '.[aws,dev]'
cp .env.runtime.example .env.runtime
# Set AWS_REGION, AWS_S3_BUCKET, LLM_PROVIDER=bedrock,
# EMBEDDING_PROVIDER=bedrock, and a Bedrock model ID enabled in your account.
```

Use an ECS task role / EC2 instance profile / IAM Identity Center credentials. For local development, use an AWS profile (`AWS_PROFILE`) and `aws sso login`; avoid long-lived IAM user keys.

Provision the document bucket and runtime roles:

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit bucket_name and the exact Bedrock model ARNs allowed in your account.
terraform init
terraform plan
terraform apply
```

Copy the `documents_bucket` output into `AWS_S3_BUCKET`. The Terraform configuration deliberately does not provision a database, VPC, ECS service, Redis cluster, or public endpoint: these require environment-specific networking, sizing, backup, ingress, and secret decisions. Deploy the existing API and worker containers to private ECS Fargate services in your approved VPC, use RDS/Aurora PostgreSQL and ElastiCache Redis, and expose the API through an ALB/API Gateway + WAF. Keep the database and cache private.

## Upload a policy document

The endpoint requires the existing `POLICY_INGEST` permission and tenant context:

```bash
curl -X POST "$API_BASE/v1/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "code=INVESTMENT-POLICY" \
  -F "version=2026.1" \
  -F "title=Investment Suitability Policy" \
  -F "file=@investment-policy.pdf;type=application/pdf"
```

The endpoint limits uploads to 20 MB and currently accepts PDF, text/plain and text/html. PDF text is extracted locally first; if extraction fails (for example, scanned PDF), the uploaded S3 object is sent to asynchronous Textract text detection. The extracted content is indexed into the existing PostgreSQL policy table and retains the S3 URI as its source reference.

## AWS model access and IAM

Enable the desired foundation models in Amazon Bedrock in the configured region. The ECS task role needs `bedrock:InvokeModel` for the exact model/inference-profile ARNs, S3 object access limited to the document bucket, and Textract job permissions. Restrict Textract `Resource: "*"` as supported by its IAM authorization model; add conditions and separate roles where possible. The Terraform sample intentionally leaves Bedrock model ARNs empty until explicitly supplied.

## Important architecture boundaries

- LangGraph remains the sole agent workflow orchestrator. Bedrock supplies model inference; it does not replace LangGraph.
- PostgreSQL remains the system of record for reviews, audit events, policy metadata and durable workflow state. S3 stores original source files.
- The current retrieval path remains custom pgvector + lexical retrieval + RRF. OpenSearch Serverless and Bedrock Knowledge Bases are documented as optional future alternatives, not silently introduced as duplicate indexes.
- Existing Celery + Redis + transactional outbox remains the local/background task mechanism. SQS, EventBridge and Step Functions are not wired into the current outbox dispatch path in this revision; migrate that path deliberately rather than running two competing queue systems.
- AgentCore Runtime/Gateway are not enabled automatically. Add them when you need independently hosted agents or managed MCP tool exposure; keep authorization and tenant checks in the application regardless.
- Bedrock Guardrails, KMS, CloudTrail, CloudWatch and X-Ray need account-level configuration and deployment wiring. The implementation guide identifies these as deployment controls, not claims that they are already active in a cloud account.

## Production checklist before handling regulated data

1. Configure VPC private subnets, VPC endpoints/egress controls, security groups, TLS and WAF.
2. Use RDS/Aurora encryption, Multi-AZ, PITR, backup retention and tested restore procedures.
3. Configure ElastiCache TLS/auth and private networking.
4. Store JWT/OIDC and database secrets in Secrets Manager; inject via ECS task definitions.
5. Add KMS CMKs if required by your data classification and key ownership policy.
6. Enable CloudTrail, GuardDuty, Security Hub, Macie and CloudWatch alarms/log retention.
7. Add Bedrock Guardrails and application-level prompt-injection defenses; neither replaces RBAC, RLS or deterministic compliance rules.
8. Validate tenant isolation, S3 key access, signed URL expiry, document deletion/retention and audit evidence.
9. Run RAG regression evaluations after every embedding, chunking, model or retrieval change.
10. Perform load, penetration, disaster-recovery and legal/compliance reviews before production use.
