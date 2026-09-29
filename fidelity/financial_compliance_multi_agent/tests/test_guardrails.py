import pytest
from app.guardrails.output_validation import validate_result
def test_unknown_citation_rejected():
    with pytest.raises(ValueError,match="unknown policy"):
        validate_result({"summary":"x","claims":[],"findings":[{"claim":"x","status":"needs_review","rationale":"x","policy_ids":[999],"policy_codes":["X"]}],"overall_risk":"medium","recommended_action":"human_review"},set())
