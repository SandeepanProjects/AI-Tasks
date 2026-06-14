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

# Sends prompt to GPT.
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# Prompt Creation
# prompt = f"""
# CONTEXT:
# {context}

# QUESTION:
# {query}
# """

# Example:

# CONTEXT:
# Machine Learning is subset of AI

# QUESTION:
# What is ML?