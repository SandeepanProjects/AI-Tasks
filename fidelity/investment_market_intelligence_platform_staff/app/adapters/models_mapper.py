from app.db.models import ReviewRow
from app.domain.models import Review, ReviewStatus

def review_from_row(row: ReviewRow) -> Review:
    return Review(tenant_id=row.tenant_id, created_by=row.created_by, question=row.question,
                  assets=row.assets, lookback_days=row.lookback_days, purpose=row.purpose,
                  id=row.id, status=ReviewStatus(row.status), report=row.report,
                  reviewer_id=row.reviewer_id, reviewer_comment=row.reviewer_comment,
                  created_at=row.created_at, version=row.version)

def review_to_row(review: Review) -> ReviewRow:
    return ReviewRow(id=review.id, tenant_id=review.tenant_id, created_by=review.created_by,
                     question=review.question, assets=review.assets, lookback_days=review.lookback_days,
                     purpose=review.purpose, status=review.status.value, report=review.report,
                     reviewer_id=review.reviewer_id, reviewer_comment=review.reviewer_comment,
                     version=review.version, created_at=review.created_at)
