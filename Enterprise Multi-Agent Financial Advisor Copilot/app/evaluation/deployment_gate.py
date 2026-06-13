class DeploymentGate:

    MIN_FAITHFULNESS = 0.85

    MIN_RELEVANCY = 0.85

    MIN_CONTEXT_PRECISION = 0.80

    MIN_CONTEXT_RECALL = 0.80


    @classmethod
    def validate(
        cls,
        result
    ):

        if (
            result["faithfulness"]
            < cls.MIN_FAITHFULNESS
        ):

            raise Exception(
                "Faithfulness below threshold"
            )

        if (
            result["answer_relevancy"]
            < cls.MIN_RELEVANCY
        ):

            raise Exception(
                "Answer relevancy below threshold"
            )

        if (
            result["context_precision"]
            < cls.MIN_CONTEXT_PRECISION
        ):

            raise Exception(
                "Context precision below threshold"
            )

        if (
            result["context_recall"]
            < cls.MIN_CONTEXT_RECALL
        ):

            raise Exception(
                "Context recall below threshold"
            )

        return True