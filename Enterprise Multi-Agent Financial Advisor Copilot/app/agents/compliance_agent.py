class ComplianceAgent:

    def run(self, state: dict):

        notes = []

        if "buy" in state["query"].lower():

            notes.append(
                "No guaranteed financial returns should be implied"
            )

        notes.append(
            "All recommendations are informational only"
        )

        state["compliance_notes"] = notes

        return state