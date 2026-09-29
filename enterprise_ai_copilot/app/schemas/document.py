from pydantic import BaseModel, Field
class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    content: str = Field(min_length=1)
class DocumentResponse(BaseModel):
    id: str
    title: str
    status: str
