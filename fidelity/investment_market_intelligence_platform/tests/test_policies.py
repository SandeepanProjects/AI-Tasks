import pytest
from app.domain.policies import validate_research_request, validate_report
from app.core.errors import GuardrailViolation

def test_request_rejects_out_of_range_lookback():
    with pytest.raises(GuardrailViolation):
        validate_research_request("BTC volatility", ["BTC"], 9999, 365)

def test_report_requires_evidence_and_limitations():
    with pytest.raises(GuardrailViolation):
        validate_report({"summary": "Analysis"})
