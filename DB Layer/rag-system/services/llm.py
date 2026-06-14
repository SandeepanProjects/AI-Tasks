# services/llm.py
# Purpose:

# Talk to GPT.

from openai import OpenAI

client = OpenAI()

def generate_answer(context, query):
    prompt = f"""
    Use the context below to answer the question.

    CONTEXT:
    {context}

    QUESTION:
    {query}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content