from ai_agents.contracts import AgentContext, AgentResult

class ComplianceResearchAgent:
    name = "compliance_research"

    async def run(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            agent=self.name,
            output={"evidence": [{
                "citation": "policy://demo/marketing-claims",
                "text": "Marketing claims must not imply guaranteed returns.",
            }]},
        )

class ComplianceWriterAgent:
    name = "compliance_writer"

    async def run(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            agent=self.name,
            output={
                "summary": f"Compliance review completed with {context.state['risk']} risk."
            },
        )
