class ReciprocalRankFusion:

    @staticmethod
    def fuse(
        vector_results,
        bm25_results,
        k=60
    ):

        scores = {}

        for rank, doc in enumerate(
            vector_results
        ):

            scores[doc] = scores.get(
                doc,
                0
            ) + 1 / (k + rank)

        for rank, doc in enumerate(
            bm25_results
        ):

            scores[doc] = scores.get(
                doc,
                0
            ) + 1 / (k + rank)

        ranked = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            doc
            for doc, _
            in ranked
        ]