import json

from app.llm.openai_client import client

from app.tools.registry import ToolRegistry


class AgentOrchestrator:
    def __init__(self):
        self.registry = ToolRegistry()

    async def run(
        self,
        user_query: str,
    ):
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a production AI agent."
                ),
            },
            {
                "role": "user",
                "content": user_query,
            },
        ]

        while True:
            response = (
                client.chat.completions.create(
                    model="gpt-5.5",
                    messages=messages,
                    tools=self.registry.get_openai_tools(),
                    tool_choice="auto",
                )
            )

            assistant_message = (
                response.choices[0].message
            )

            messages.append(
                assistant_message
            )

            tool_calls = (
                assistant_message.tool_calls
            )

            if not tool_calls:
                return assistant_message.content

            for tool_call in tool_calls:
                tool_name = (
                    tool_call.function.name
                )

                arguments = json.loads(
                    tool_call.function.arguments
                )

                tool = self.registry.get_tool(
                    tool_name
                )

                if not tool:
                    raise Exception(
                        f"Tool not found: {tool_name}"
                    )

                result = await tool.execute(
                    **arguments
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": json.dumps(result),
                    }
                )