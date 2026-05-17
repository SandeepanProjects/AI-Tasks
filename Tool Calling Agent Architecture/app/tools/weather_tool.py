from app.tools.base import BaseTool


class WeatherTool(BaseTool):
    name = "get_weather"

    description = (
        "Get current weather for a city"
    )

    parameters = {
        "type": "object",
        "properties": {
            "city": {
                "type": "string"
            }
        },
        "required": ["city"],
    }

    async def execute(
        self,
        city: str,
    ):
        """
        Replace with real weather API.
        """

        return {
            "city": city,
            "temperature": "28C",
            "condition": "Cloudy",
        }