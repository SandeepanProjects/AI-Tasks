class HybridSearch:

    @staticmethod
    def build_filter(
        metadata_filter: dict
    ):

        if not metadata_filter:
            return None

        must_conditions = []

        for key, value in metadata_filter.items():

            must_conditions.append(
                {
                    "key": key,
                    "match": {
                        "value": value
                    }
                }
            )

        return {
            "must": must_conditions
        }