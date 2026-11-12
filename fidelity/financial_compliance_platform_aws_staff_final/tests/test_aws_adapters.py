from app.aws.storage import S3DocumentStore


def test_s3_key_is_tenant_scoped_and_filename_is_sanitized(monkeypatch):
    monkeypatch.setattr("app.aws.storage.settings.aws_s3_prefix", "compliance-documents")
    store = S3DocumentStore("example-bucket")
    key = store.build_key("tenant_123", "../../Quarterly policy (final).pdf")
    assert key.startswith("compliance-documents/tenant_123/")
    assert ".." not in key
    assert "Quarterly_policy_final_.pdf" in key


def test_s3_key_rejects_untrusted_tenant_identifier():
    store = S3DocumentStore("example-bucket")
    try:
        store.build_key("tenant/other", "policy.pdf")
    except ValueError as exc:
        assert "tenant" in str(exc)
    else:
        raise AssertionError("unsafe tenant identifier was accepted")
