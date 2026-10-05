import pytest
from app.domain.policies import validate_research_request, validate_report
from app.core.errors import GuardrailViolation
def test_request_bounds():
    with pytest.raises(GuardrailViolation): validate_research_request("BTC",["BTC"],9999,365)
def test_citation_integrity():
    with pytest.raises(GuardrailViolation):
        validate_report({"summary":"x","evidence_ids":["evil"],"limitations":["x"]},{"valid"})
