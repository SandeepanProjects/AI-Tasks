class ReportAgent:

    def run(self, state: dict):

        report = f"""
FINANCIAL ADVISORY REPORT

Query: {state['query']}

--- PORTFOLIO ANALYSIS ---
{state.get('portfolio_analysis', {})}

--- MARKET RESEARCH ---
{state.get('research', '')}

--- RISK ANALYSIS ---
{state.get('risk_analysis', '')}

--- COMPLIANCE NOTES ---
{state.get('compliance_notes', [])}

DISCLAIMER:
This is not financial advice.
"""

        state["final_report"] = report

        return state