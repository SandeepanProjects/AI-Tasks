"""Textract asynchronous PDF OCR adapter for documents already uploaded to S3."""
from __future__ import annotations
import asyncio
import time
from app.aws.clients import client
from app.config import settings


class TextractS3OCRProvider:
    async def extract_s3(self, bucket: str, key: str) -> str:
        textract = client("textract")
        started = await asyncio.to_thread(textract.start_document_text_detection,
            DocumentLocation={"S3Object": {"Bucket": bucket, "Name": key}})
        job_id = started["JobId"]
        deadline = time.monotonic() + settings.aws_textract_max_wait_seconds
        next_token = None
        lines: list[str] = []
        while time.monotonic() < deadline:
            kwargs = {"JobId": job_id}
            if next_token:
                kwargs["NextToken"] = next_token
            result = await asyncio.to_thread(textract.get_document_text_detection, **kwargs)
            status = result.get("JobStatus")
            if status == "FAILED":
                raise RuntimeError("Textract document text detection failed")
            if status == "IN_PROGRESS":
                await asyncio.sleep(settings.aws_textract_poll_seconds)
                continue
            lines.extend(block.get("Text", "") for block in result.get("Blocks", [])
                         if block.get("BlockType") == "LINE" and block.get("Text"))
            next_token = result.get("NextToken")
            if not next_token:
                return "\n".join(lines)
        raise TimeoutError("Textract job exceeded AWS_TEXTRACT_MAX_WAIT_SECONDS")
