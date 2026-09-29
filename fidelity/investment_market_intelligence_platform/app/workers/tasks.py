from app.workers.celery_app import celery_app

@celery_app.task(name="app.workers.tasks.ingest_source", autoretry_for=(TimeoutError,),
                 retry_backoff=True, retry_jitter=True, max_retries=4)
def ingest_source(source_key: str, tenant_id: str) -> dict:
    # Implement a licensed connector with SSRF protection, allow-listed hosts,
    # content-type/size limits, robots/contract compliance, and provenance.
    # Idempotency key should include tenant + provider + source document ID/version.
    if not source_key or not tenant_id:
        raise ValueError("source_key and tenant_id are required")
    return {"status": "accepted", "source_key": source_key, "tenant_id": tenant_id,
            "note": "Connector stub: no network fetch performed"}
