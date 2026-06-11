class Reranker:

    @staticmethod
    def rerank(
        results: list,
        query: str
    ):

        for r in results:

            score = r["score"]

            text = r["text"].lower()

            # heuristic boost
            if "risk" in query.lower() and "risk" in text:
                score += 0.05

            if "portfolio" in query.lower() and "allocation" in text:
                score += 0.03

            r["final_score"] = score

        return sorted(
            results,
            key=lambda x: x["final_score"],
            reverse=True
        )