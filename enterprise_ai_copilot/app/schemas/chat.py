from pydantic import BaseModel, Field
class ChatRequest(BaseModel):
    thread_id: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=8000)
