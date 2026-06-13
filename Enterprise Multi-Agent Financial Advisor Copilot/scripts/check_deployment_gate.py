from app.evaluation.deployment_gate import (
    DeploymentGate
)

sample_result = {

    "faithfulness": 0.92,

    "answer_relevancy": 0.91,

    "context_precision": 0.89,

    "context_recall": 0.88
}

DeploymentGate.validate(
    sample_result
)

print(
    "Deployment Gate Passed"
)