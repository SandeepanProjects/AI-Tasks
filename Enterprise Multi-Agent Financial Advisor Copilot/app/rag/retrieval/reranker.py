# class Reranker:

#     @staticmethod
#     def rerank(
#         results: list,
#         query: str
#     ):

#         for r in results:

#             score = r["score"]

#             text = r["text"].lower()

#             # heuristic boost
#             if "risk" in query.lower() and "risk" in text:
#                 score += 0.05

#             if "portfolio" in query.lower() and "allocation" in text:
#                 score += 0.03

#             r["final_score"] = score

#         return sorted(
#             results,
#             key=lambda x: x["final_score"],
#             reverse=True
#         )


from sentence_transformers import (
    CrossEncoder
)


class Reranker:

    def __init__(self):

        self.model = CrossEncoder(
            "BAAI/bge-reranker-base"
        )


    def rerank(
        self,
        query,
        docs,
        top_k=5
    ):

        pairs = [
            [query, doc]
            for doc in docs
        ]

        scores = self.model.predict(
            pairs
        )

        ranked = sorted(
            zip(docs, scores),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            doc
            for doc, _
            in ranked[:top_k]
        ]