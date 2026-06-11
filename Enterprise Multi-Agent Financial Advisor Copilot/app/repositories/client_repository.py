from sqlalchemy.orm import Session

from app.models.client import Client


class ClientRepository:

    @staticmethod
    def create(
        db: Session,
        client: Client
    ):

        db.add(client)

        db.commit()

        db.refresh(client)

        return client