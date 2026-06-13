from rank_bm25 import BM25Okapi


class BM25Retriever:

    def __init__(
        self,
        documents
    ):

        self.documents = documents

        tokenized = [
            doc.split()
            for doc in documents
        ]

        self.bm25 = BM25Okapi(
            tokenized
        )


    def search(
        self,
        query: str,
        top_k=20
    ):

        scores = self.bm25.get_scores(
            query.split()
        )

        ranked = sorted(
            zip(
                self.documents,
                scores
            ),
            key=lambda x: x[1],
            reverse=True
        )

        return ranked[:top_k]