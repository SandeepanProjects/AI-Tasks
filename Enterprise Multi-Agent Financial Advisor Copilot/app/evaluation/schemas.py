from pydantic import BaseModel


class EvaluationSample(BaseModel):
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str


class EvaluationResult(BaseModel):
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float