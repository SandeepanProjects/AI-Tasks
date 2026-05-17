class PromptBuilder:
    def build_prompt(self, query, contexts):
        context_text = "\n\n".join(contexts)

        return f"""
You are an enterprise AI assistant.

Answer ONLY using the provided context.

If the answer is not present, say:
'I could not find the answer in the documents.'

Context:
{context_text}

Question:
{query}
"""