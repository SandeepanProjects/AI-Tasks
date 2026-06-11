from app.rag.evaluation.metrics import Metrics
from app.rag.evaluation.hallucination import HallucinationDetector
from app.rag.evaluation.ragas_adapter import RAGASAdapter


class Evaluator:

    def evaluate_retrieval(
        self,
        retrieved,
        expected
    ):

        return {
            "precision@k": Metrics.precision_at_k(
                retrieved,
                expected
            ),
            "recall@k": Metrics.recall_at_k(
                retrieved,
                expected
            )
        }


    def evaluate_answer(
        self,
        answer,
        context
    ):

        hallucination = (
            HallucinationDetector.detect(
                answer,
                context
            )
        )

        return {
            "hallucination": hallucination,
            "faithfulness": RAGASAdapter.faithfulness(
                answer,
                context
            )
        }


    def evaluate_context(
        self,
        question,
        context
    ):

        return {
            "context_relevance":
                RAGASAdapter.context_relevance(
                    question,
                    context
                )
        }