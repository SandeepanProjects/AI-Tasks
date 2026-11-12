import pytest
from app.guardrails import validate


def test_rejects_wrong_tenant_policy_evidence():
    policies = [
        {
            "id": "p1",
            "tenant_id": "tenant-a",
            "code": "C",
            "version": "1",
            "text": "Actual source quote",
        }
    ]
    findings = [
        {
            "category": "risk",
            "severity": "high",
            "statement": "x",
            "rationale": "y",
            "evidence": [
                {
                    "policy_id": "p2",
                    "policy_code": "C",
                    "policy_version": "1",
                    "quote": "Actual source quote",
                }
            ],
        }
    ]
    with pytest.raises(ValueError):
        validate(findings, policies, "tenant-a")


def test_rejects_non_exact_quote():
    policies = [
        {
            "id": "p1",
            "tenant_id": "tenant-a",
            "code": "C",
            "version": "1",
            "text": "Actual source quote",
        }
    ]
    findings = [
        {
            "category": "risk",
            "severity": "high",
            "statement": "x",
            "rationale": "y",
            "evidence": [
                {
                    "policy_id": "p1",
                    "policy_code": "C",
                    "policy_version": "1",
                    "quote": "invented quote",
                }
            ],
        }
    ]
    with pytest.raises(ValueError):
        validate(findings, policies, "tenant-a")
