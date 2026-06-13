# import mlflow


# class MLflowTracker:

#     def __init__(self):

#         mlflow.set_tracking_uri(
#             "http://localhost:5000"
#         )


#     def log_rag_run(
#         self,
#         question,
#         answer,
#         metrics
#     ):

#         with mlflow.start_run():

#             mlflow.log_param(
#                 "question",
#                 question
#             )

#             mlflow.log_metric(
#                 "faithfulness",
#                 metrics.get(
#                     "faithfulness",
#                     0
#                 )
#             )

#             mlflow.log_metric(
#                 "context_relevance",
#                 metrics.get(
#                     "context_relevance",
#                     0
#                 )
#             )

#             mlflow.log_text(
#                 answer,
#                 "answer.txt"
#             )






# pip install mlflow
import mlflow

from app.config.settings import (
    settings
)


class MLflowTracker:

    def __init__(self):

        mlflow.set_tracking_uri(
            settings.MLFLOW_TRACKING_URI
        )


    def log_chat(
        self,
        question,
        answer,
        latency
    ):

        with mlflow.start_run():

            mlflow.log_param(
                "question",
                question
            )

            mlflow.log_metric(
                "latency",
                latency
            )

            mlflow.log_text(
                answer,
                "answer.txt"
            )