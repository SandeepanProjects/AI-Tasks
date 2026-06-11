from app.llm.provider import get_llm


llm = get_llm()


def rewrite_query(question: str):

    prompt = f"""
    Rewrite the query
    for semantic retrieval.

    Query:
    {question}
    """

    return llm.invoke(prompt).content