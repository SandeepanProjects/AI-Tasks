from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
from sqlalchemy import select
from app.config import settings
from app.db.session import Session
from app.db.models import Review, Policy
from app.retrieval.ingestion import OpenAIEmbedder
from app.retrieval.strategies import KeywordStrategy, VectorStrategy, FallbackStrategy
from app.graph.workflow import Workflow
from langgraph.types import Command


async def _loader(tenant_id, query):
    async with Session() as db:
        keyword = KeywordStrategy()
        try:
            vector = VectorStrategy(OpenAIEmbedder())
            strategy = FallbackStrategy(vector, keyword)
        except RuntimeError:
            strategy = keyword
        rows = await strategy.retrieve(db, tenant_id, query, 6)
        return [
            {
                "id": p.id,
                "tenant_id": p.tenant_id,
                "code": p.code,
                "version": p.version,
                "title": p.title,
                "text": p.text,
            }
            for p in rows
        ]


def _thread(review_id):
    return f"review:{review_id}"


async def invoke_review(tenant_id, review_id, decision=None):
    pool = AsyncConnectionPool(
        conninfo=settings.sync_database_url, min_size=1, max_size=4, open=False
    )
    await pool.open()
    try:
        async with AsyncPostgresSaver(pool) as checkpointer:
            await checkpointer.setup()
            workflow = Workflow(_loader, checkpointer)
            config = {"configurable": {"thread_id": _thread(review_id)}}
            async with Session() as db:
                review = await db.scalar(
                    select(Review).where(
                        Review.id == review_id, Review.tenant_id == tenant_id
                    )
                )
                if not review:
                    raise LookupError("Review not found")
                statement = review.input_text
            if decision is None:
                result = await workflow.graph.ainvoke(
                    {
                        "review_id": review_id,
                        "tenant_id": tenant_id,
                        "statement": statement,
                        "max_steps": settings.max_agent_steps,
                        "max_reworks": settings.max_evaluation_reworks,
                    },
                    config=config,
                )
            else:
                result = await workflow.graph.ainvoke(
                    Command(resume=decision), config=config
                )
            async with Session() as db:
                review = await db.scalar(
                    select(Review).where(
                        Review.id == review_id, Review.tenant_id == tenant_id
                    )
                )
                if review:
                    review.status = result.get("status", "needs_human")
                    review.result_json = result.get("final_result")
                    await db.commit()
            return {
                "review_id": review_id,
                "status": result.get("status", "needs_human"),
            }
    finally:
        await pool.close()
