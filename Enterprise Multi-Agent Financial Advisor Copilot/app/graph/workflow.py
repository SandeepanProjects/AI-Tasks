# import asyncio


# async def parallel_agents(
#     state
# ):

#     results = await asyncio.gather(

#         risk_agent.run(state),

#         research_agent.run(state),

#         compliance_agent.run(state)
#     )

#     return {

#         "risk": results[0],

#         "research": results[1],

#         "compliance": results[2]
#     }

import asyncio

from langgraph.graph import StateGraph
from langgraph.graph import END

from app.graph.state import (
    FinancialAdvisorState
)

from app.agents.risk_agent import (
    RiskAgent
)

from app.agents.research_agent import (
    ResearchAgent
)

from app.agents.compliance_agent import (
    ComplianceAgent
)

from app.agents.report_agent import (
    ReportAgent
)


class FinancialAdvisorWorkflow:

    def __init__(
        self,
        llm
    ):

        self.risk_agent = RiskAgent(
            llm
        )

        self.research_agent = (
            ResearchAgent(llm)
        )

        self.compliance_agent = (
            ComplianceAgent(llm)
        )

        self.report_agent = (
            ReportAgent(llm)
        )

        self.graph = self.build()


    async def parallel_analysis(
        self,
        state: FinancialAdvisorState
    ):

        risk_task = (
            self.risk_agent.run(state)
        )

        research_task = (
            self.research_agent.run(state)
        )

        compliance_task = (
            self.compliance_agent.run(
                state
            )
        )

        (
            risk_result,
            research_result,
            compliance_result
        ) = await asyncio.gather(
            risk_task,
            research_task,
            compliance_task
        )

        state["risk_analysis"] = (
            risk_result
        )

        state["market_research"] = (
            research_result
        )

        state["compliance_review"] = (
            compliance_result
        )

        return state


    async def generate_report(
        self,
        state: FinancialAdvisorState
    ):

        final_report = (
            await self.report_agent.run(
                state
            )
        )

        state["final_response"] = (
            final_report
        )

        return state


    def build(self):

        workflow = StateGraph(
            FinancialAdvisorState
        )

        workflow.add_node(
            "parallel_analysis",
            self.parallel_analysis
        )

        workflow.add_node(
            "generate_report",
            self.generate_report
        )

        workflow.set_entry_point(
            "parallel_analysis"
        )

        workflow.add_edge(
            "parallel_analysis",
            "generate_report"
        )

        workflow.add_edge(
            "generate_report",
            END
        )

        return workflow.compile()


    async def invoke(
        self,
        query: str,
        user_id: str,
        tenant_id: str
    ):

        state = {

            "query": query,

            "user_id": user_id,

            "tenant_id": tenant_id,

            "retrieved_docs": [],

            "risk_analysis": None,

            "market_research": None,

            "compliance_review": None,

            "final_response": None,

            "metadata": {}
        }

        result = await self.graph.ainvoke(
            state
        )

        return result