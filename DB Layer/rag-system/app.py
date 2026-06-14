# app.py

from fastapi import FastAPI
from services.rag_pipeline import rag_pipeline

app = FastAPI() # Creates web application.

@app.post("/chat") # Creates REST endpoint.
def chat(user_id: str, query: str):
    response = rag_pipeline(user_id, query)
    return {"response": response}