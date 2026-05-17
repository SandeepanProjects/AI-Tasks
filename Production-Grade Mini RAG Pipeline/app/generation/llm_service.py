from openai import OpenAI
from app.core.config import settings


client = OpenAI(api_key=settings.OPENAI_API_KEY)


class LLMService:
    def generate(self, prompt):
        response = client.chat.completions.create(
            model=settings.CHAT_MODEL,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful RAG assistant.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        return response.choices[0].message.content
