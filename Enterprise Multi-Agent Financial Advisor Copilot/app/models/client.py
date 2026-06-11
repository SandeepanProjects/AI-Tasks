from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer

from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Client(Base):

    __tablename__ = "clients"

    id = Column(
        String,
        primary_key=True
    )

    name = Column(
        String,
        nullable=False
    )

    age = Column(
        Integer,
        nullable=False
    )

    risk_profile = Column(
        String,
        nullable=False
    )