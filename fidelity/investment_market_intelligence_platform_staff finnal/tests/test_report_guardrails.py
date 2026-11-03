import pytest
from app.domain.policies import validate_report
from app.core.errors import GuardrailViolation


def test_valid_report_requires_known_citations_and_limitations():
    report = {"summary": "Evidence indicates elevated volatility.", "observations": ["Volatility increased."],
        "risks": ["Liquidity risk"], "evidence_ids": ["e-1"], "limitations": ["Historical data only."]}
    validate_report(report, {"e-1"})


def test_report_rejects_unknown_citation():
    report = {"summary": "Summary", "observations": [], "risks": [],
        "evidence_ids": ["outside-tenant-id"], "limitations": ["Limited data."]}
    with pytest.raises(GuardrailViolation):
        validate_report(report, {"e-1"})


def test_report_rejects_extra_fields():
    report = {"summary": "Summary", "observations": [], "risks": [],
        "evidence_ids": ["e-1"], "limitations": ["Limited data."], "buy": "yes"}
    with pytest.raises(GuardrailViolation):
        validate_report(report, {"e-1"})
