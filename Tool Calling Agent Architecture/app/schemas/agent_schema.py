# app/schemas/agent_schema.py

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field


class AgentRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=10000,
    )

    conversation_id: Optional[str] = None


class ToolCall(BaseModel):
    tool_name: str

    arguments: Dict[str, Any]


class ToolResult(BaseModel):
    tool_name: str

    result: Dict[str, Any]


class AgentResponse(BaseModel):
    response: str

    tool_calls: List[ToolCall] = []

    tool_results: List[ToolResult] = []

    execution_time_ms: Optional[float] = None


class HealthResponse(BaseModel):
    status: str

    version: str


class ErrorResponse(BaseModel):
    error: str

    detail: Optional[str] = None

