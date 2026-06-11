class RiskAgent:

    def run(self, state: dict):

        portfolio = state.get(
            "portfolio_analysis",
            {}
        )

        risk = portfolio.get("risk", "UNKNOWN")

        state["risk_analysis"] = (
            f"Overall portfolio risk is {risk}"
        )

        return state