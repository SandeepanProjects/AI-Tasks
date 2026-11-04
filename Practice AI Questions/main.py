from fastapi import FastAPI
from routers.apirouter import router as saree_router

app = FastAPI(title="Saree E-Commerce API", version="1.0.0")

# Include the saree router with a prefix or directly
app.include_router(saree_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Saree API. Visit /docs for interactive documentation."}
