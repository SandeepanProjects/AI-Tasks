from typing import Literal

AgentType = Literal[
    "rag",
    "sql",
    "memory",
    "general"
]


def route_task(question: str) -> AgentType:

    question = question.lower()

    if any(
        keyword in question
        for keyword in [
            "database",
            "sql",
            "table",
            "postgres"
        ]
    ):
        return "sql"

    if any(
        keyword in question
        for keyword in [
            "policy",
            "document",
            "manual",
            "knowledge"
        ]
    ):
        return "rag"

    if any(
        keyword in question
        for keyword in [
            "remember",
            "history",
            "previous"
        ]
    ):
        return "memory"

    return "general"