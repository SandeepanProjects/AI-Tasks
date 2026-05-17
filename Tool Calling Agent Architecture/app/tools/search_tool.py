from app.tools.base import BaseTool


class SearchTool(BaseTool):
    name = "search"

    description = (
        "Search the web"
    )

    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string"
            }
        },
        "required": ["query"],
    }

    async def execute(
        self,
        query: str,
    ):
        """
        Replace with real search engine.
        """

        return {
            "results": [
                f"Search result for {query}"
            ]
        }