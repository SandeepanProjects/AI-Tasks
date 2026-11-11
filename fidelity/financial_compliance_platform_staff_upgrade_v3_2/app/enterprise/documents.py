"""Document intake primitives. OCR is injected so deployments can use an approved vendor."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Protocol
import re

@dataclass(frozen=True)
class ExtractedDocument:
    text: str
    media_type: str
    sha256: str
    page_count: int
    classification: str

@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    text: str
    page: int | None
    section: str | None
    source_hash: str
    start_char: int
    end_char: int

class OCRProvider(Protocol):
    async def extract(self, content: bytes, media_type: str) -> str: ...

class DocumentIntake:
    ALLOWED = {"text/plain", "text/html", "application/pdf"}
    def __init__(self, *, max_bytes: int = 20_000_000, ocr: OCRProvider | None = None):
        self.max_bytes, self.ocr = max_bytes, ocr

    async def parse(self, content: bytes, filename: str, media_type: str) -> ExtractedDocument:
        if not content or len(content) > self.max_bytes:
            raise ValueError("empty document or size limit exceeded")
        if media_type not in self.ALLOWED:
            raise ValueError("unsupported media type")
        digest = sha256(content).hexdigest()
        pages = 1
        if media_type == "text/plain":
            text = content.decode("utf-8-sig", errors="strict")
        elif media_type == "text/html":
            raw = content.decode("utf-8", errors="strict")
            text = re.sub(r"<[^>]+>", " ", raw)
            text = re.sub(r"\s+", " ", text).strip()
        else:
            try:
                from pypdf import PdfReader
                import io
                reader = PdfReader(io.BytesIO(content), strict=True)
                pages = len(reader.pages)
                text = "\n".join((page.extract_text() or "") for page in reader.pages)
            except Exception as exc:
                raise ValueError("PDF parsing failed; route scanned PDFs through the configured OCR provider") from exc
            if not text.strip() and self.ocr:
                text = await self.ocr.extract(content, media_type)
        if not text.strip():
            raise ValueError("document contains no extractable text")
        classification = self.classify(text, filename)
        return ExtractedDocument(text, media_type, digest, pages, classification)

    @staticmethod
    def classify(text: str, filename: str = "") -> str:
        sample = (filename + " " + text[:5000]).casefold()
        if any(x in sample for x in ("investment policy", "compliance policy", "regulatory requirement")):
            return "policy"
        if any(x in sample for x in ("portfolio", "holdings", "asset allocation", "ticker")):
            return "portfolio_statement"
        if any(x in sample for x in ("marketing material", "performance claim", "investment recommendation")):
            return "advisory_communication"
        return "unclassified"

    @staticmethod
    def chunk(document: ExtractedDocument, *, chunk_size: int = 1800, overlap: int = 250) -> list[DocumentChunk]:
        if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
            raise ValueError("invalid chunk configuration")
        text = document.text
        chunks, start, index = [], 0, 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            if end < len(text):
                boundary = text.rfind("\n", start, end)
                if boundary > start + chunk_size // 2:
                    end = boundary
            piece = text[start:end].strip()
            if piece:
                chunks.append(DocumentChunk(f"{document.sha256[:12]}-{index}", piece, None, None,
                                            document.sha256, start, end))
                index += 1
            if end >= len(text): break
            start = max(end - overlap, start + 1)
        return chunks
