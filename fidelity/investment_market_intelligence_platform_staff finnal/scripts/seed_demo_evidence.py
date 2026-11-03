import asyncio, hashlib, uuid
from datetime import datetime, timezone
from sqlalchemy import text, select
from app.db.session import SessionLocal
from app.db.models import EvidenceChunkRow
from app.adapters.embeddings import build_embedding_provider

async def main():
    content = ("Illustrative market research fixture for BTC Bitcoin digital assets. Digital assets are volatile and "
               "risk factors include liquidity, volatility and market structure. Historical performance does not guarantee future results. This fixture "
               "is for local development only and is not licensed market data.")
    embedder = build_embedding_provider()
    vector = await embedder.embed(content)
    async with SessionLocal() as session:
        await session.execute(text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
                              {"tenant_id": "demo-tenant"})
        source_uri = "fixture://demo/001"
        digest = hashlib.sha256(f"{source_uri}\0{content}".encode()).hexdigest()
        exists = await session.scalar(select(EvidenceChunkRow.id).where(
            EvidenceChunkRow.tenant_id == "demo-tenant", EvidenceChunkRow.content_hash == digest))
        if not exists:
            session.add(EvidenceChunkRow(id=uuid.uuid4(), tenant_id="demo-tenant", source_name="demo",
                source_uri=source_uri, observed_at=datetime.now(timezone.utc),
                content=content, content_hash=digest, embedding=vector,
                metadata_json={"kind": "fixture", "live": False}))
            await session.commit()

if __name__ == "__main__":
    asyncio.run(main())
