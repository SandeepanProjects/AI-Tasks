from hashlib import sha256
from uuid import uuid4
from openai import AsyncOpenAI
from sqlalchemy import select, update
from app.config import settings
from app.db.models import Policy

class OpenAIEmbedder:
    def __init__(self):
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required")
        if settings.embedding_dimensions != 1536:
            raise RuntimeError("Database vector dimension is 1536; configure EMBEDDING_DIMENSIONS=1536 or migrate the vector column")
        self.client = AsyncOpenAI(api_key=settings.openai_api_key, timeout=30.0, max_retries=2)

    async def embed_query(self, text):
        response = await self.client.embeddings.create(model=settings.embedding_model, input=text, dimensions=settings.embedding_dimensions)
        return response.data[0].embedding

    async def embed_documents(self, texts):
        vectors = []
        for start in range(0, len(texts), 64):
            response = await self.client.embeddings.create(model=settings.embedding_model, input=texts[start:start+64], dimensions=settings.embedding_dimensions)
            vectors.extend(item.embedding for item in response.data)
        return vectors

def get_embedder():
    """Select the configured embedding provider without changing retrieval callers."""
    if settings.embedding_provider.lower() == "bedrock":
        from app.aws.bedrock_embeddings import BedrockEmbedder
        return BedrockEmbedder()
    if settings.embedding_provider.lower() != "openai":
        raise RuntimeError("EMBEDDING_PROVIDER must be 'openai' or 'bedrock'")
    return OpenAIEmbedder()


async def ingest_policy(db, tenant_id, code, version, title, text, source_uri=None):
    document_hash = sha256(text.encode("utf-8")).hexdigest()
    existing = list((await db.scalars(select(Policy).where(
        Policy.tenant_id == tenant_id, Policy.code == code, Policy.version == version
    ).order_by(Policy.chunk_index))).all())
    if existing:
        if all(row.document_hash == document_hash for row in existing):
            return existing
        raise ValueError("A different document already exists for this policy code and version")
    # Retain historical versions, but only the newly ingested version is active.
    await db.execute(update(Policy).where(Policy.tenant_id == tenant_id, Policy.code == code).values(active=False))
    chunks = [text[i:i+3000] for i in range(0, len(text), 2500)]
    vectors = await get_embedder().embed_documents(chunks)
    created = []
    for index, (chunk, vector) in enumerate(zip(chunks, vectors)):
        row = Policy(id=uuid4().hex, tenant_id=tenant_id, code=code, version=version,
            title=f"{title} [chunk {index+1}/{len(chunks)}]", text=chunk, active=True,
            embedding=vector, document_hash=document_hash, chunk_index=index, source_uri=source_uri)
        db.add(row); created.append(row)
    await db.flush()
    return created
