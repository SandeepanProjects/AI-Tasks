from dataclasses import dataclass


@dataclass
class EvaluationMetrics:
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float

    @property
    def overall_score(self):

        return (
            self.faithfulness
            + self.answer_relevancy
            + self.context_precision
            + self.context_recall
        ) / 4