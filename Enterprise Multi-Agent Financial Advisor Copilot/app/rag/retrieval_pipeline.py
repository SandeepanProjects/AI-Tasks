from app.rag.reranker import (
    Reranker
)

from app.rag.fusion import (
    ReciprocalRankFusion
)


class RetrievalPipeline:

    def __init__(

        self,

        vectorstore,

        bm25
    ):

        self.vectorstore = vectorstore

        self.bm25 = bm25

        self.reranker = Reranker()


    async def retrieve(

        self,

        query,

        query_vector
    ):

        vector_results = (
            await self.vectorstore.search(
                query_vector,
                top_k=30
            )
        )

        vector_docs = [

            r.payload["text"]

            for r in vector_results
        ]

        bm25_docs = [

            doc

            for doc, _ in self.bm25.search(
                query,
                top_k=30
            )
        ]

        fused_docs = (
            ReciprocalRankFusion.fuse(
                vector_docs,
                bm25_docs
            )
        )

        final_docs = (
            self.reranker.rerank(
                query,
                fused_docs,
                top_k=5
            )
        )

        return final_docs