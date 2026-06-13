class ModelRouter:

    def choose_model(
        self,
        query
    ):

        words = len(
            query.split()
        )

        if words > 1000:

            return "gpt-4o"

        return "gpt-4o-mini"