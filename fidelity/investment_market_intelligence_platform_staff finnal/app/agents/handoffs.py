from enum import StrEnum
class HandoffTarget(StrEnum):
    RESEARCH="research"; PORTFOLIO_RISK="portfolio_risk"; EVIDENCE_REVIEW="evidence_review"

def choose_handoff(question: str) -> list[HandoffTarget]:
    q=question.lower()
    targets=[HandoffTarget.RESEARCH]
    if any(k in q for k in ("portfolio","allocation","drawdown","risk","bitcoin","btc")):
        targets.append(HandoffTarget.PORTFOLIO_RISK)
    targets.append(HandoffTarget.EVIDENCE_REVIEW)
    return targets
