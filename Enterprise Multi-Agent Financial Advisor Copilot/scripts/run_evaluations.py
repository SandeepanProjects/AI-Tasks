from app.evaluation.service import (
    EvaluationService
)


service = EvaluationService()

datasets = [

    "app/evaluation/datasets/portfolio_questions.json",

    "app/evaluation/datasets/retirement_questions.json",

    "app/evaluation/datasets/risk_questions.json"
]

for dataset in datasets:

    result = service.run_dataset(
        dataset
    )

    print(result)