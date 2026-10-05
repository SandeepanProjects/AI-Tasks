from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.adapters.repositories import SqlReviewRepository, SqlAuditRepository

def get_review_repository(session: AsyncSession = Depends(get_session)):
    return SqlReviewRepository(session)

def get_audit_repository(session: AsyncSession = Depends(get_session)):
    return SqlAuditRepository(session)
