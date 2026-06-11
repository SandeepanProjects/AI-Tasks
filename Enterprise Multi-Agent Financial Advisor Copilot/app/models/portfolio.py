from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import JSON

from app.models.client import Base


class Portfolio(Base):

    __tablename__ = "portfolios"

    id = Column(
        String,
        primary_key=True
    )

    client_id = Column(
        String,
        nullable=False
    )

    holdings = Column(
        JSON,
        nullable=False
    )