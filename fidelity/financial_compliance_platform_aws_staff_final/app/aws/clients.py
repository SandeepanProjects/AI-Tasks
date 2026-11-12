"""Lazy boto3 client factory; importing the application does not require AWS credentials."""
from functools import lru_cache

from app.config import settings


@lru_cache(maxsize=8)
def client(service_name: str):
    try:
        import boto3
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise RuntimeError("AWS integrations require the 'aws' optional dependencies: pip install -e '.[aws]'") from exc
    return boto3.client(service_name, region_name=settings.aws_region)
