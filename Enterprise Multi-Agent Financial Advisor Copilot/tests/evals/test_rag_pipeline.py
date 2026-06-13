from app.evaluation.deployment_gate import (
    DeploymentGate
)


def test_evaluation_thresholds():

    result = {

        "faithfulness": 0.9,

        "answer_relevancy": 0.9,

        "context_precision": 0.9,

        "context_recall": 0.9
    }

    assert (
        DeploymentGate.validate(
            result
        )
        is True
    )