from pydantic import BaseModel
from typing import List


class EvaluationSample(BaseModel):

    question: str

    ground_truth_answer: str

    expected_docs: List[str]