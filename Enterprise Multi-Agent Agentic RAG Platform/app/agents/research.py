from app.llm.provider import get_llm

llm = get_llm()


def research_node(state):

    prompt = f"""
You are an expert AI assistant.

Question:
{state["question"]}

Retrieved Context:
{state["context"]}

Answer using ONLY retrieved context.

If answer not present,
say information unavailable.
"""

    response = llm.invoke(prompt)

    state["answer"] = response.content

    return state