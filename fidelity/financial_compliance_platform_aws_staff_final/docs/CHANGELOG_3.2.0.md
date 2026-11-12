# 3.2.0 — Staff capability implementation pack

- Added a content-adaptive planner with an allowlisted task catalogue and bounded task budget; wired the planner into LangGraph and made evaluation expectations follow selected specialists.
- Added text/HTML/PDF intake, content classification, configurable chunking, and an OCR provider contract for scanned PDFs.
- Added immutable evidence provenance records, quote hashes, tenant-scoped SQL persistence and an RLS migration.
- Added structured semantic claim assessment, confidence-based abstention and pairwise contradiction checks with an OpenAI judge adapter.
- Added deterministic portfolio exposure summaries and linear scenario stress sensitivity.
- Added policy version diffing and human-review reassessment candidate generation.
- Added least-privilege read-only connector contracts, HTTPS host allowlisting, permission checks and OIDC/JWKS verification.
- Added optional OpenTelemetry OTLP trace bootstrap, Locust load script and a staging fault-injection drill plan.
- Added capability status documentation that explicitly identifies components not yet connected to the main API/graph or external enterprise systems.
