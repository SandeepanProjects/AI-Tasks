from fastapi import FastAPI

from app.api.routes.chat import router


app = FastAPI(
    title="Enterprise Agentic RAG"
)

app.include_router(router)