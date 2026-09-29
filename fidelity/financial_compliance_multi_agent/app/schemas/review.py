from typing import Literal, Any
from pydantic import BaseModel, Field
class ReviewCreate(BaseModel):
    tenant_id: str="demo"
    content: str=Field(min_length=5,max_length=50000)
class DecisionRequest(BaseModel):
    decision: Literal["approved","rejected"]
    comment: str=Field(min_length=3,max_length=4000)
class ReviewRead(BaseModel):
    id: str; tenant_id: str; submitted_by: str; content: str; status: str
    result: dict[str,Any]|None=None
    decision_comment: str|None=None
    decided_by: str|None=None
