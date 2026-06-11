from app.mlops.mlflow.tracking import MLflowTracker


class RAGExperiment:

    def __init__(self):

        self.tracker = MLflowTracker()


    def log(self, result):

        self.tracker.log_rag_run(

            question=result["question"],

            answer=result["answer"],

            metrics={
                "faithfulness":
                result.get("faithfulness", 0),

                "context_relevance":
                result.get(
                    "context_relevance",
                    0
                )
            }
        )