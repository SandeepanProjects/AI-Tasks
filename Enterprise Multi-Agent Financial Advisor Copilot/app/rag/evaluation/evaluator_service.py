class EvaluationService:

    def __init__(self):

        self.evaluator = Evaluator()

    def run_full_eval(
        self,
        sample,
        retrieved,
        answer,
        context
    ):

        retrieval_metrics = (
            self.evaluator.evaluate_retrieval(
                retrieved,
                sample.expected_docs
            )
        )

        answer_metrics = (
            self.evaluator.evaluate_answer(
                answer,
                context
            )
        )

        context_metrics = (
            self.evaluator.evaluate_context(
                sample.question,
                context
            )
        )

        return {
            "question": sample.question,

            "retrieval_metrics":
                retrieval_metrics,

            "answer_metrics":
                answer_metrics,

            "context_metrics":
                context_metrics
        }