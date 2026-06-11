from app.graph.workflow import graph


def ask_question(question: str):

    result = graph.invoke(
        {
            "question": question
        }
    )

    return result["answer"]