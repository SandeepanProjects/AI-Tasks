from app.llm.provider import get_llm

llm = get_llm()


def critic_node(state):

    prompt = f"""
    Review answer for:

    - Hallucination
    - Missing facts
    - Accuracy

    Answer:
    {state['answer']}
    """

    critique = llm.invoke(prompt).content

    state["critique"] = critique

    return state