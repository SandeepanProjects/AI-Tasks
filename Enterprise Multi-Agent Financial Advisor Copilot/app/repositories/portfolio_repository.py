from sqlalchemy.orm import Session

from app.models.portfolio import Portfolio


class PortfolioRepository:

    @staticmethod
    def create(
        db: Session,
        portfolio: Portfolio
    ):

        db.add(portfolio)

        db.commit()

        db.refresh(portfolio)

        return portfolio