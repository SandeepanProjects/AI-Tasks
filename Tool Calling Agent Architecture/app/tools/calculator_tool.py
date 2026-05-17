from app.tools.base import BaseTool


class CalculatorTool(BaseTool):
    name = "calculator"

    description = (
        "Perform mathematical calculations"
    )

    parameters = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string"
            }
        },
        "required": ["expression"],
    }

    async def execute(
        self,
        expression: str,
    ):
        result = eval(expression)

        return {
            "expression": expression,
            "result": result,
        }