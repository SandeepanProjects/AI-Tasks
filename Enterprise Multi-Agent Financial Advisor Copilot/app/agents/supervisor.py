class SupervisorAgent:

    def route(self, state: dict):

        query = state["query"].lower()

        routes = []

        if "portfolio" in query:
            routes.append("portfolio")

        if "risk" in query:
            routes.append("risk")

        if "market" in query:
            routes.append("research")

        if "compliance" in query:
            routes.append("compliance")

        if not routes:
            routes = ["research"]

        return routes
    
    
    
    class SupervisorAgent:

    async def run(
        self,
        state
    ):

        query = (
            state["query"]
            .lower()
        )

        tasks = []

        if "risk" in query:
            tasks.append(
                risk_agent.run(state)
            )

        if "market" in query:
            tasks.append(
                research_agent.run(state)
            )

        if "compliance" in query:
            tasks.append(
                compliance_agent.run(state)
            )

        return await asyncio.gather(
            *tasks
        )