import json
from pathlib import Path

from app.evaluation.ragas_runner import (
    RagasRunner
)

from app.evaluation.report_generator import (
    EvaluationReportGenerator
)


class EvaluationService:

    def __init__(self):

        self.runner = RagasRunner()

        self.reporter = (
            EvaluationReportGenerator()
        )


    def load_dataset(
        self,
        path: str
    ):

        with open(path) as f:

            return json.load(f)


    def run_dataset(
        self,
        dataset_path: str
    ):

        data = self.load_dataset(
            dataset_path
        )

        result = self.runner.run(data)

        self.reporter.generate(
            result
        )

        return result