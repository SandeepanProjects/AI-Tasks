class PortfolioAgent:

    def run(self, state: dict):

        portfolio = state.get("portfolio_data", {})

        tech_weight = sum(
            v for k, v in portfolio.items()
            if "tech" in k.lower()
        )

        state["portfolio_analysis"] = {
            "tech_exposure": tech_weight,
            "risk": "HIGH" if tech_weight > 60 else "MEDIUM"
        }

        return state