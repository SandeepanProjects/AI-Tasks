from pydantic import BaseModel


class ClientCreate(BaseModel):

    id: str

    name: str

    age: int

    risk_profile: str


class ClientResponse(ClientCreate):
    pass