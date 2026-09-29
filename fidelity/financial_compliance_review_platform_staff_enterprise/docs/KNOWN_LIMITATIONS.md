# Known limitations — do not skip

This is an advanced reference project, not a turnkey regulated deployment.

1. The starter API surface in the supplied v2 archive is incomplete; inspect `app/main.py` and add
   endpoint wiring appropriate to your deployment. The new RBAC module is a reusable policy seam.
2. Configure tenant context inside the same transaction as each protected query. RLS policies
   require this and a non-owner runtime role. Test under actual PostgreSQL roles.
3. The existing workflow needs integration validation for your exact LangGraph/checkpointer version.
   Exercise interrupt → process restart → authorized resume with a real PostgreSQL checkpointer.
4. Add separation-of-duties and idempotent decision persistence before production.
5. The sample model/retrieval logic requires evaluation, prompt-injection testing, cost controls,
   timeouts, and provider outage handling.
6. A production event pipeline should use a transactional outbox; Celery tasks must be idempotent.
