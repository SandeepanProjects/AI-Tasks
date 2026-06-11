class HumanApprovalService:

    def requires_review(
        self,
        hallucination_score: float
    ) -> bool:

        return hallucination_score > 0.7


approval_service = HumanApprovalService()