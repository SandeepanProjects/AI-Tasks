from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Financial Compliance Review Platform", version="2.0.0")
app.include_router(router, prefix="/api/v1")
