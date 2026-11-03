from app.agents.graph import build_graph, ResearchWorkflow
from app.agents.tools import ResearchTools
from app.adapters.llm import MockChatModel, OpenAICompatibleChatModel
from app.adapters.embeddings import build_embedding_provider
from app.adapters.repositories import SqlEvidenceRepository, SqlCheckpointRepository
from app.core.config import settings
from app.db.session import SessionLocal

class SessionEvidenceRepository:
    def __init__(self):
        self.embedder = build_embedding_provider()

    async def search(self, tenant_id, query, limit, lookback_days):
        async with SessionLocal() as session:
            repo = SqlEvidenceRepository(session)
            if settings.mock_mode:
                # Hash embeddings are deliberately non-semantic; use PostgreSQL full-text search in demo mode.
                return await repo.search(tenant_id, query, limit, lookback_days)
            embedding = await self.embedder.embed(query)
            return await repo.search_by_embedding(tenant_id, embedding, limit, lookback_days)

class SessionCheckpointRepository:
    async def save(self, tenant_id, review_id,node,state):
        async with SessionLocal() as session:
            await SqlCheckpointRepository(session).save(tenant_id, review_id,node,state)

def build_workflow():
    evidence=SessionEvidenceRepository()
    tools=ResearchTools(evidence, settings.max_tool_calls, settings.max_context_chunks)
    if settings.mock_mode:
        model = MockChatModel()
    elif not (settings.llm_base_url and settings.llm_api_key and
              settings.llm_api_key.get_secret_value().strip() and settings.llm_model):
        raise RuntimeError("MOCK_MODE=false requires LLM_BASE_URL, LLM_API_KEY and LLM_MODEL")
    else:
        model=OpenAICompatibleChatModel(settings.llm_base_url,settings.llm_api_key.get_secret_value(),
                                        settings.llm_model,settings.request_timeout_seconds)
    graph=build_graph(tools, model)
    return ResearchWorkflow(graph,SessionCheckpointRepository())
