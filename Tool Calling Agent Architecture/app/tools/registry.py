from app.tools.weather_tool import (
    WeatherTool,
)

from app.tools.search_tool import (
    SearchTool,
)

from app.tools.calculator_tool import (
    CalculatorTool,
)


class ToolRegistry:
    def __init__(self):
        self.tools = {
            "get_weather": WeatherTool(),
            "search": SearchTool(),
            "calculator": CalculatorTool(),
        }

    def get_tool(self, name):
        return self.tools.get(name)

    def get_openai_tools(self):
        return [
            tool.openai_schema()
            for tool in self.tools.values()
        ]