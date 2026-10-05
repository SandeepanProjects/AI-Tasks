from app.agents.graph import build_graph, ResearchWorkflow
from app.agents.tools import ResearchTools
from app.adapters.llm import MockChatModel, OpenAICompatibleChatModel
from app.adapters.embeddings import DeterministicEmbeddingProvider
from app.adapters.repositories import SqlEvidenceRepository, SqlCheckpointRepository
from app.core.config import settings
from app.db.session import SessionLocal

class SessionEvidenceRepository:
    def __init__(self):
        self.embedder = DeterministicEmbeddingProvider()

    async def search(self, tenant_id, query, limit):
        async with SessionLocal() as session:
            repo = SqlEvidenceRepository(session)
            embedding = await self.embedder.embed(query)
            semantic = await repo.search_by_embedding(tenant_id, embedding, limit)
            # Graceful fallback for documents ingested before embeddings were populated.
            return semantic or await repo.search(tenant_id, query, limit)

class SessionCheckpointRepository:
    async def save(self, review_id,node,state):
        async with SessionLocal() as session:
            await SqlCheckpointRepository(session).save(review_id,node,state)

def build_workflow():
    evidence=SessionEvidenceRepository()
    tools=ResearchTools(evidence,settings.max_tool_calls)
    if settings.mock_mode or not (settings.llm_base_url and settings.llm_api_key and settings.llm_model):
        model=MockChatModel()
    else:
        model=OpenAICompatibleChatModel(settings.llm_base_url,settings.llm_api_key.get_secret_value(),
                                        settings.llm_model,settings.request_timeout_seconds)
    graph=build_graph(tools,model,SessionCheckpointRepository())
    return ResearchWorkflow(graph,SessionCheckpointRepository())
