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