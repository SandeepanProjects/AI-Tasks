"""Embedding adapters. Hash embeddings are deterministic test fixtures, never production retrieval."""
from __future__ import annotations

import hashlib
import math
from typing import Protocol

import httpx

from app.core.config import settings


class EmbeddingProvider(Protocol):
    async def embed(self, text: str) -> list[float]: ...


class DeterministicEmbeddingProvider:
    """Non-semantic deterministic adapter for local tests and offline demos only."""
    async def embed(self, text: str) -> list[float]:
        dim = settings.embedding_dimensions
        seed = hashlib.sha512(text.encode("utf-8")).digest()
        values = [((seed[i % len(seed)] / 255.0) * 2.0) - 1.0 for i in range(dim)]
        norm = math.sqrt(sum(v * v for v in values)) or 1.0
        return [v / norm for v in values]


class OpenAICompatibleEmbeddingProvider:
    """OpenAI-compatible /embeddings adapter with strict dimension validation."""
    def __init__(self, base_url: str, api_key: str, model: str,
                 dimensions: int = 384, timeout: float = 20.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.dimensions = dimensions
        self.timeout = timeout

    async def embed(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("Embedding input cannot be empty")
        payload = {"model": self.model, "input": text, "dimensions": self.dimensions}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/embeddings", json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"})
            response.raise_for_status()
            vector = response.json()["data"][0]["embedding"]
        if len(vector) != self.dimensions:
            raise ValueError(f"Embedding dimension mismatch: expected {self.dimensions}, got {len(vector)}")
        if not all(math.isfinite(float(v)) for v in vector):
            raise ValueError("Embedding contains non-finite values")
        return [float(v) for v in vector]


def build_embedding_provider() -> EmbeddingProvider:
    if settings.mock_mode:
        return DeterministicEmbeddingProvider()
    if not (settings.llm_base_url and settings.llm_api_key and
            settings.llm_api_key.get_secret_value().strip() and settings.embedding_model):
        raise RuntimeError("Configure LLM_BASE_URL, LLM_API_KEY and EMBEDDING_MODEL, or enable MOCK_MODE")
    return OpenAICompatibleEmbeddingProvider(
        settings.llm_base_url, settings.llm_api_key.get_secret_value(),
        settings.embedding_model, settings.embedding_dimensions, settings.request_timeout_seconds)
