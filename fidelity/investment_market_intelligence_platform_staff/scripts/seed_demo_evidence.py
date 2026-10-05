import asyncio, hashlib, uuid
from datetime import datetime, timezone
from app.db.session import SessionLocal
from app.db.models import EvidenceChunkRow

async def main():
    async with SessionLocal() as s:
        content=("Illustrative market research fixture. Digital assets are volatile and "
                 "historical performance does not guarantee future results.")
        s.add(EvidenceChunkRow(id=uuid.uuid4(),tenant_id="demo-tenant",source_name="demo",
            source_uri="fixture://demo/001",observed_at=datetime.now(timezone.utc),
            content=content,content_hash=hashlib.sha256(content.encode()).hexdigest(),
            embedding=None,metadata_json={"kind":"fixture","live":False}))
        await s.commit()
if __name__=="__main__": asyncio.run(main())
