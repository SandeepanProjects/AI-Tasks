import pytest
from ai_llm.mock import MockLLM
from investment_intelligence.services.analysis_service import InvestmentAnalysisService

@pytest.mark.asyncio
async def test_analysis():
    result = await InvestmentAnalysisService(MockLLM()).analyze(
        "t1", "What are the major risks?", "BTC"
    )
    assert result["status"] == "completed"
    assert result["evidence_count"] == 1
