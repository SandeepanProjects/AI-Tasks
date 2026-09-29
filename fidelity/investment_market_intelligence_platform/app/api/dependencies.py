from app.application.use_cases import ReviewService
from app.adapters.in_memory import InMemoryReviewRepository, FixtureEvidenceRepository
from app.adapters.llm import MockChatModel
from app.agents.tools import ResearchTools
from app.agents.graph import build_graph, LangGraphResearchWorkflow

_repo = InMemoryReviewRepository()
_evidence = FixtureEvidenceRepository()
_tools = ResearchTools(_evidence)
_graph = build_graph(_tools, MockChatModel())
_service = ReviewService(_repo, LangGraphResearchWorkflow(_graph))

def get_review_service() -> ReviewService:
    return _service
