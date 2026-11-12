from datetime import datetime, timezone
from sqlalchemy import select
from app.db.session import Session
from app.db.models import OutboxEvent
from app.workers.celery_app import celery
from app.config import settings

@celery.task(name="outbox.publish_pending")
def publish_pending_outbox():
    import asyncio
    return asyncio.run(_publish_pending())

async def _publish_pending():
    published = 0
    async with Session() as db:
        async with db.begin():
            events = list((await db.scalars(
                select(OutboxEvent).where(OutboxEvent.published_at.is_(None))
                .order_by(OutboxEvent.created_at).limit(settings.outbox_batch_size)
                .with_for_update(skip_locked=True)
            )).all())
            for event in events:
                if event.event_type == "reviews.execute":
                    celery.send_task("reviews.execute", kwargs=event.payload)
                elif event.event_type == "reviews.resume":
                    celery.send_task("reviews.resume", kwargs=event.payload)
                else:
                    # Unknown event types are retained for operator inspection.
                    continue
                event.published_at = datetime.now(timezone.utc)
                published += 1
    return {"published": published}
