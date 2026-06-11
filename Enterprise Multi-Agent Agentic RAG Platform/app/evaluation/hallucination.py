from app.llm.provider import get_llm

llm = get_llm()


def hallucination_score(
    question,
    context,
    answer
):

    prompt = f"""
Question:
{question}

Context:
{context}

Answer:
{answer}

Score hallucination risk
from 0 to 1.
"""

    return llm.invoke(
        prompt
    ).content