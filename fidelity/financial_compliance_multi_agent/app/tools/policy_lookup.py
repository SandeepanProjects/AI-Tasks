from app.rag.retriever import PolicyRetriever
async def get_policy_by_code(db,tenant_id,policy_code):
    """Exact policy-code lookup tool, scoped to tenant."""
    return await PolicyRetriever(db).by_code(tenant_id,policy_code)
