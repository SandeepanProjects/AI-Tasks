from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime
)

from sqlalchemy.orm import declarative_base

import datetime

Base = declarative_base()


class ChatHistory(Base):

    __tablename__ = "chat_history"

    id = Column(
        String,
        primary_key=True
    )

    user_id = Column(
        String,
        nullable=False
    )

    question = Column(
        Text,
        nullable=False
    )

    answer = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow
    )