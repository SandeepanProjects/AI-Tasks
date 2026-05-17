ALLOWED_TOOLS = {
    "get_weather",
    "search",
    "calculator",
}


def validate_tool(tool_name):
    if tool_name not in ALLOWED_TOOLS:
        raise Exception(
            f"Unauthorized tool: {tool_name}"
        )