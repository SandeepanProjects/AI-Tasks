from pydantic import BaseModel, Field
class PolicyCreate(BaseModel):
    tenant_id: str="demo"
    policy_code: str
    title: str
    text: str=Field(min_length=10)
