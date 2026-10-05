from dataclasses import dataclass

@dataclass(frozen=True)
class ComplianceReview:
    risk: str
    rationale: str
    requires_human_approval: bool

def classify_risk(text: str) -> str:
    high_risk_terms = ("guaranteed", "risk-free", "guarantee", "no risk")
    return "high" if any(t in text.lower() for t in high_risk_terms) else "medium"
