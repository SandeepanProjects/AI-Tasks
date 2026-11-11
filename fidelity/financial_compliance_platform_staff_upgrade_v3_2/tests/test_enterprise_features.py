import pytest
from app.enterprise.planning import AdaptivePlanner
from app.enterprise.documents import DocumentIntake
from app.enterprise.evidence import EvidenceLedger, EvidenceRecord
from app.enterprise.portfolio import Holding, PortfolioAnalytics
from app.enterprise.policy_impact import PolicyImpactAnalyzer


def test_adaptive_planner_selects_only_relevant_specialists():
    plan = AdaptivePlanner().plan("The portfolio has high risk and annualized return claims with fees")
    kinds = {t.kind for t in plan.tasks}
    assert {"risk", "performance", "fees", "policy_research", "claim_verification"} <= kinds
    assert plan.risk_tier in {"medium", "high"}


def test_planner_rejects_untrusted_tool_proposal():
    with pytest.raises(ValueError):
        AdaptivePlanner.validate_proposal([{"kind": "delete_customer_records"}])


@pytest.mark.asyncio
async def test_document_pipeline_text_and_chunking():
    doc = await DocumentIntake().parse(b"Investment policy\n" + b"A" * 3000, "policy.txt", "text/plain")
    chunks = DocumentIntake.chunk(doc, chunk_size=1000, overlap=100)
    assert doc.classification == "policy"
    assert len(chunks) >= 3 and all(c.source_hash == doc.sha256 for c in chunks)


def test_evidence_ledger_is_tenant_scoped_and_immutable():
    record = EvidenceRecord.create(evidence_id="e1", tenant_id="t1", document_id="d1", document_version="v1",
        chunk_id="c1", quote="approved claim", start_char=0, end_char=14, retrieval_method="hybrid", retrieval_score=.9)
    ledger = EvidenceLedger(); ledger.append(record)
    assert ledger.get("e1", tenant_id="t1") == record
    with pytest.raises(PermissionError): ledger.get("e1", tenant_id="t2")


def test_portfolio_stress_is_deterministic():
    holdings = [Holding("ABC", 700, "equity", "tech", "US", 1.2), Holding("BOND", 300, "fixed_income", "govt", "US")]
    exposure = PortfolioAnalytics.exposures(holdings)
    stress = PortfolioAnalytics.stress_test(holdings, {"equity_selloff": {"equity": -.2, "fixed_income": .02}})
    assert exposure["largest_position_weight"] == .7
    assert stress["scenarios"]["equity_selloff"]["estimated_pnl"] == -162.0


def test_policy_impact_candidates_require_human_reassessment():
    change = PolicyImpactAnalyzer.compare("P1", "1", "Claims must disclose fees", "2", "Claims must disclose all fees and risks")
    candidates = PolicyImpactAnalyzer.candidates(change, [{"artifact_id": "a1", "content": "Our claims disclose all fees"}])
    assert candidates and candidates[0]["requires_human_review"] is True
