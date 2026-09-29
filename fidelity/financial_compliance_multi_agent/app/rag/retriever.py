from sqlalchemy import select, or_
from app.models.policy import PolicyChunk
from app.rag.embeddings import EmbeddingService
from app.cache.redis_client import cache_get,cache_set
class PolicyRetriever:
    def __init__(self,db): self.db=db; self.embeddings=EmbeddingService()
    async def search(self,tenant_id,query,limit=5):
        # Tenant included in cache key. Use stable key digest rather than Python's randomized hash.
        import hashlib
        digest=hashlib.sha256(query.encode()).hexdigest()[:24]
        key=f"policy-search:{tenant_id}:{digest}:{limit}"
        cached=await cache_get(key)
        if cached is not None: return cached
        vector=await self.embeddings.embed(query)
        stmt=select(PolicyChunk).where(PolicyChunk.tenant_id==tenant_id)
        if vector: stmt=stmt.order_by(PolicyChunk.embedding.cosine_distance(vector)).limit(limit)
        else:
            terms=[t for t in query.lower().split() if len(t)>3][:8]
            if terms: stmt=stmt.where(or_(*[PolicyChunk.text.ilike(f"%{t}%") for t in terms]))
            stmt=stmt.limit(limit)
        rows=(await self.db.execute(stmt)).scalars().all()
        result=[{"policy_id":r.id,"policy_code":r.policy_code,"title":r.title,"text":r.text,"excerpt":r.text[:1200]} for r in rows]
        await cache_set(key,result); return result
    async def by_code(self,tenant_id,code):
        rows=(await self.db.execute(select(PolicyChunk).where(PolicyChunk.tenant_id==tenant_id,PolicyChunk.policy_code==code))).scalars().all()
        return [{"policy_id":r.id,"policy_code":r.policy_code,"title":r.title,"text":r.text,"excerpt":r.text[:1200]} for r in rows]
