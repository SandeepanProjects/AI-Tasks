from app.core.errors import GuardrailViolation

PROHIBITED_CLAIMS = ("guaranteed return", "risk-free profit", "certain to rise")

def validate_research_request(question: str, assets: list[str], lookback_days: int, max_days: int) -> None:
    if not question.strip() or len(question) > 4000:
        raise GuardrailViolation("Question must contain 1–4000 characters.")
    if not assets or len(assets) > 20:
        raise GuardrailViolation("Provide between 1 and 20 assets.")
    if lookback_days < 1 or lookback_days > max_days:
        raise GuardrailViolation(f"lookback_days must be between 1 and {max_days}.")
    if any(not a.replace("-", "").isalnum() for a in assets):
        raise GuardrailViolation("Asset symbols contain unsupported characters.")

def validate_report(report: dict) -> None:
    text = str(report).lower()
    if any(phrase in text for phrase in PROHIBITED_CLAIMS):
        raise GuardrailViolation("Report contains prohibited certainty/return language.")
    citations = report.get("evidence_ids", [])
    if not citations:
        raise GuardrailViolation("Report must cite at least one evidence item.")
    if not report.get("limitations"):
        raise GuardrailViolation("Report must state limitations and uncertainty.")
