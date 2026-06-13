from time import perf_counter

from app.mlops.mlflow_tracker import (
    MLflowTracker
)

from app.observability.metrics import (
    AI_REQUESTS,
    AI_LATENCY
)

from app.observability.tracing import (
    traced
)

from app.memory.retrieval_cache import (
    RetrievalCache
)


class ChatService:

    def __init__(
        self,
        retrieval_pipeline,
        llm,
        embedder
    ):

        self.pipeline = retrieval_pipeline

        self.llm = llm

        self.embedder = embedder

        self.cache = RetrievalCache()

        self.mlflow = MLflowTracker()


    @traced("chat_service")
    async def chat(
        self,
        question: str
    ):

        start = perf_counter()

        AI_REQUESTS.inc()

        cached = await self.cache.get(
            question
        )

        if cached:

            return cached

        vector = await self.embedder.embed(
            question
        )

        docs = await self.pipeline.retrieve(
            question,
            vector
        )

        context = "\n".join(docs)

        answer = await self.llm.generate(
            question,
            context
        )

        result = {
            "answer": answer,
            "sources": docs
        }

        await self.cache.set(
            question,
            result
        )

        latency = (
            perf_counter() - start
        )

        AI_LATENCY.observe(
            latency
        )

        self.mlflow.log_chat(
            question,
            answer,
            latency
        )

        return result