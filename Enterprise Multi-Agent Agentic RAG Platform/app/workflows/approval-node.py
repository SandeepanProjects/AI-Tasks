from app.workflows.approval import (
    approval_service
)


def approval_node(state):

    score = state[
        "hallucination_score"
    ]

    state[
        "requires_human_review"
    ] = (
        approval_service.requires_review(
            score
        )
    )

    return state