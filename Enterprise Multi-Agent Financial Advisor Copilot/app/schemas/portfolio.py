from pydantic import BaseModel


class PortfolioCreate(BaseModel):

    id: str

    client_id: str

    holdings: dict


class PortfolioResponse(PortfolioCreate):
    pass