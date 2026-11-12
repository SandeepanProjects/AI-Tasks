"""Tenant-scoped S3 document storage adapter."""
from __future__ import annotations
import asyncio
import re
from pathlib import PurePath
from uuid import uuid4
from app.aws.clients import client
from app.config import settings


def _safe_name(filename: str) -> str:
    name = PurePath(filename or "document").name
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    return (name or "document")[:120]


class S3DocumentStore:
    def __init__(self, bucket: str | None = None):
        self.bucket = bucket or settings.aws_s3_bucket
        if not self.bucket:
            raise RuntimeError("AWS_S3_BUCKET must be configured to use S3 document storage")

    def build_key(self, tenant_id: str, filename: str) -> str:
        if not tenant_id or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", tenant_id):
            raise ValueError("invalid tenant identifier")
        return f"{settings.aws_s3_prefix.strip('/')}/{tenant_id}/{uuid4().hex}-{_safe_name(filename)}".lstrip("/")

    async def put(self, tenant_id: str, filename: str, content: bytes, content_type: str) -> dict:
        if not content:
            raise ValueError("empty document")
        key = self.build_key(tenant_id, filename)
        args = {"Bucket": self.bucket, "Key": key, "Body": content,
                "ContentType": content_type, "Metadata": {"tenant-id": tenant_id}}
        if settings.aws_kms_key_id:
            args.update(ServerSideEncryption="aws:kms", SSEKMSKeyId=settings.aws_kms_key_id)
        # Otherwise rely on the bucket's default encryption (SSE-S3 or SSE-KMS).
        await asyncio.to_thread(client("s3").put_object, **args)
        return {"bucket": self.bucket, "key": key, "s3_uri": f"s3://{self.bucket}/{key}"}

    async def presigned_get(self, tenant_id: str, key: str, expires_seconds: int = 300) -> str:
        prefix = f"{settings.aws_s3_prefix.strip('/')}/{tenant_id}/".lstrip("/")
        if not key.startswith(prefix) or ".." in key.split("/"):
            raise PermissionError("document is outside the caller tenant prefix")
        return await asyncio.to_thread(client("s3").generate_presigned_url, "get_object",
            Params={"Bucket": self.bucket, "Key": key}, ExpiresIn=min(max(expires_seconds, 60), 900))
