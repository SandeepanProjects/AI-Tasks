from app.rag.evaluation.evaluator_service import EvaluationService

service = EvaluationService()

result = service.run_full_eval(
    sample=dataset[0],
    retrieved=[
        {"id": "doc1"},
        {"id": "doc2"}
    ],
    answer="Portfolio risk is high due to volatility.",
    context="Portfolio risk is defined as..."
)

print(result)