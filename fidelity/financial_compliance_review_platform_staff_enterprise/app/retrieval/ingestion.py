from uuid import uuid4
from openai import AsyncOpenAI
from sqlalchemy import select
from app.config import settings
from app.db.models import Policy


class OpenAIEmbedder:
    def __init__(self):
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required")
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def embed_query(self, text):
        r = await self.client.embeddings.create(
            model=settings.embedding_model,
            input=text,
            dimensions=settings.embedding_dimensions,
        )
        return r.data[0].embedding

    async def embed_documents(self, texts):
        r = await self.client.embeddings.create(
            model=settings.embedding_model,
            input=texts,
            dimensions=settings.embedding_dimensions,
        )
        return [x.embedding for x in r.data]


async def ingest_policy(db, tenant_id, code, version, title, text):
    embedder = OpenAIEmbedder()
    chunks = [text[i : i + 3000] for i in range(0, len(text), 2500)]
    vectors = await embedder.embed_documents(chunks)
    # Store chunked records with stable policy code/version; all retrieval is tenant-scoped.
    created = []
    for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
        row = Policy(
            id=uuid4().hex,
            tenant_id=tenant_id,
            code=code,
            version=version,
            title=f"{title} [chunk {i+1}/{len(chunks)}]",
            text=chunk,
            active=True,
            embedding=vector,
        )
        db.add(row)
        created.append(row)
    await db.flush()
    return created
