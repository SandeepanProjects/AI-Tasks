import pytest
from app.guardrails import validate, GuardrailViolation


def test_cross_tenant_evidence_rejected():
    f = {
        "category": "risk",
        "severity": "high",
        "statement": "s",
        "rationale": "r",
        "evidence": [
            {
                "policy_id": "p",
                "policy_code": "C",
                "policy_version": "1",
                "quote": "quote",
            }
        ],
    }
    with pytest.raises(GuardrailViolation):
        validate(
            [f],
            [
                {
                    "id": "p",
                    "tenant_id": "other",
                    "code": "C",
                    "version": "1",
                    "text": "quote",
                }
            ],
            "tenant",
        )
