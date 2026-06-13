import pandas as pd


class EvaluationReportGenerator:

    def generate(
        self,
        results
    ):

        df = pd.DataFrame(
            [results]
        )

        df.to_excel(
            "evaluation_report.xlsx",
            index=False
        )

        return True