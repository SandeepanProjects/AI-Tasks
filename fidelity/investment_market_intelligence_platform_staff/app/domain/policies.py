from datetime import datetime, timezone
from app.core.errors import GuardrailViolation
from app.domain.models import Evidence

PROHIBITED_CLAIMS = ("guaranteed return", "risk-free profit", "certain to rise", "guaranteed profit")

def validate_research_request(question, assets, lookback_days, max_days):
    if not question or not question.strip() or len(question) > 4000:
        raise GuardrailViolation("Question must contain 1–4000 characters.")
    if not assets or len(assets) > 20:
        raise GuardrailViolation("Provide 1–20 assets.")
    if lookback_days < 1 or lookback_days > max_days:
        raise GuardrailViolation(f"lookback_days must be between 1 and {max_days}.")
    if any(not a.replace("-", "").replace(".", "").isalnum() for a in assets):
        raise GuardrailViolation("Asset symbols contain unsupported characters.")

def validate_report(report: dict, allowed_evidence_ids: set[str]):
    text = str(report).lower()
    if any(p in text for p in PROHIBITED_CLAIMS):
        raise GuardrailViolation("Report contains prohibited certainty/return language.")
    citations = report.get("evidence_ids", [])
    if not citations or not set(citations).issubset(allowed_evidence_ids):
        raise GuardrailViolation("Report citations must reference retrieved evidence.")
    if not report.get("limitations"):
        raise GuardrailViolation("Report must state limitations and uncertainty.")

def validate_evidence_freshness(evidence: list[Evidence], max_age_days: int = 7):
    now = datetime.now(timezone.utc)
    stale = [e.evidence_id for e in evidence if (now - e.observed_at).days > max_age_days]
    return stale
