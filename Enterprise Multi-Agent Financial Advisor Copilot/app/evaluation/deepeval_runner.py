from deepeval.metrics import AnswerRelevancyMetric

from deepeval.test_case import LLMTestCase


class DeepEvalRunner:

    def evaluate(
        self,
        question: str,
        actual_answer: str
    ):

        metric = AnswerRelevancyMetric(
            threshold=0.8
        )

        test_case = LLMTestCase(
            input=question,
            actual_output=actual_answer
        )

        metric.measure(test_case)

        return metric.score