from app.models.policy import PolicyChunk
from app.rag.embeddings import EmbeddingService
async def ingest_policy(db,tenant_id,policy_code,title,text):
    # Paragraph chunking is intentionally simple; use token-aware chunking for long manuals.
    chunks=[p.strip() for p in text.split("\n\n") if p.strip()] or [text]
    embedder=EmbeddingService(); rows=[]
    for i,chunk in enumerate(chunks):
        row=PolicyChunk(tenant_id=tenant_id,policy_code=policy_code,title=title if len(chunks)==1 else f"{title} (chunk {i+1})",text=chunk,embedding=await embedder.embed(chunk))
        db.add(row); rows.append(row)
    await db.commit()
    for row in rows: await db.refresh(row)
    return rows
