"""Small AWS dependency checks used by the readiness endpoint when enabled."""
import asyncio
from app.config import settings
from app.aws.clients import client

async def check_s3() -> bool:
    if not settings.aws_s3_bucket:
        return False
    await asyncio.to_thread(client("s3").head_bucket, Bucket=settings.aws_s3_bucket)
    return True
