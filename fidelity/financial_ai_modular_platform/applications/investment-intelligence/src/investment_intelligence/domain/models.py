from dataclasses import dataclass

@dataclass(frozen=True)
class InvestmentQuestion:
    question: str
    asset: str

def risk_label(asset: str) -> str:
    return "high" if asset.upper() in {"BTC", "ETH"} else "medium"
