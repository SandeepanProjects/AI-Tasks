from app.rag.retriever import PolicyRetriever
async def search_policies(db,tenant_id,query,limit=5):
    """Tenant-scoped semantic/keyword policy retrieval tool."""
    return await PolicyRetriever(db).search(tenant_id,query,limit)
