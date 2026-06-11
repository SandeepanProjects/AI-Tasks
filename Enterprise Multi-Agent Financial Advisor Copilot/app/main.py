from fastapi import FastAPI

from app.api.v1.health import router as health_router

from app.rag.api.rag_routes import router as rag_router


app = FastAPI(
    title="Financial Advisor Copilot"
)

app.include_router(health_router)

app.include_router(rag_router)