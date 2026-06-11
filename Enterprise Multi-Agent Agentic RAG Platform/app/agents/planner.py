from app.llm.provider import get_llm


llm = get_llm()


def planner_node(state):

    question = state["question"]

    prompt = f"""
    Create a concise execution plan
    for the following question.

    Question:
    {question}
    """

    plan = llm.invoke(prompt).content

    state["plan"] = plan

    return state