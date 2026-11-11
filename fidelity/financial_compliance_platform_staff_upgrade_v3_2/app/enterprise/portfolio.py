"""Deterministic portfolio exposure and scenario stress calculations (not investment advice)."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Holding:
    symbol: str
    market_value: float
    asset_class: str
    sector: str = "unknown"
    country: str = "unknown"
    beta: float = 1.0

class PortfolioAnalytics:
    @staticmethod
    def exposures(holdings: list[Holding]) -> dict:
        total = sum(max(0.0, h.market_value) for h in holdings)
        if total <= 0: raise ValueError("portfolio market value must be positive")
        def aggregate(key):
            result = {}
            for h in holdings: result[getattr(h, key)] = result.get(getattr(h, key), 0.0) + h.market_value / total
            return {k: round(v, 6) for k, v in sorted(result.items())}
        return {"total_market_value": round(total, 2), "asset_allocation": aggregate("asset_class"),
                "sector_exposure": aggregate("sector"), "country_exposure": aggregate("country"),
                "largest_position_weight": round(max(h.market_value for h in holdings) / total, 6)}

    @staticmethod
    def stress_test(holdings: list[Holding], scenarios: dict[str, dict[str, float]]) -> dict:
        """Scenario maps asset_class -> shock fraction; P&L is linear approximation."""
        if not holdings: raise ValueError("holdings required")
        results = {}
        for name, shocks in scenarios.items():
            pnl = 0.0
            for h in holdings:
                shock = shocks.get(h.asset_class, 0.0)
                if not -1.0 <= shock <= 1.0: raise ValueError("scenario shocks must be between -100% and +100%")
                pnl += h.market_value * shock * (h.beta if h.asset_class == "equity" else 1.0)
            base = sum(h.market_value for h in holdings)
            results[name] = {"estimated_pnl": round(pnl, 2), "estimated_return": round(pnl / base, 6)}
        return {"method": "linear_scenario_sensitivity", "not_a_forecast": True, "scenarios": results}
