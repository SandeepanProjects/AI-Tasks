
# app/agents/planner.py


from openai import OpenAI

from app.core.config import settings


client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)


class Planner:
    """
    Task decomposition planner.

    Advanced agents break
    complex tasks into smaller tasks.
    """

    SYSTEM_PROMPT = """
You are an AI planning engine.

Break complex user requests into
step-by-step executable tasks.

Return concise numbered steps.
"""

    async def create_plan(
        self,
        user_query: str,
    ):
        response = (
            client.chat.completions.create(
                model="gpt-5.5",
                messages=[
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": user_query,
                    },
                ],
                temperature=0,
            )
        )

        return (
            response
            .choices[0]
            .message
            .content
        )