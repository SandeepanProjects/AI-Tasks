from typing import TypedDict


class AgentState(TypedDict):

    question: str

    route: str

    plan: str

    context: str

    answer: str

    critique: str

    hallucination_score: float

    requires_human_review: bool