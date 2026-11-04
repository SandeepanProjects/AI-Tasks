from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# Initialize APIRouter
router = APIRouter(
    prefix="/sarees",
    tags=["sarees"]
)

# Pydantic model for Saree
class Saree(BaseModel):
    id: int
    name: str
    fabric: str
    color: str
    price: float
    in_stock: bool = True

# In-memory "database"
fake_saree_db: List[Saree] = [
    Saree(id=1, name="Banarasi Silk", fabric="Silk", color="Red", price=12000.0, in_stock=True),
    Saree(id=2, name="Kanjeevaram Royal", fabric="Silk", color="Green", price=15000.0, in_stock=True),
    Saree(id=3, name="Chanderi Cotton", fabric="Cotton", color="Blue", price=4500.0, in_stock=False),
]

@router.get("/", response_model=List[Saree])
async def get_sarees(fabric: Optional[str] = None):
    if fabric:
        return [saree for saree in fake_saree_db if saree.fabric.lower() == fabric.lower()]
    return fake_saree_db

@router.get("/{saree_id}", response_model=Saree)
async def get_saree_by_id(saree_id: int):
    for saree in fake_saree_db:
        if saree.id == saree_id:
            return saree
    raise HTTPException(status_code=404, type="Saree not found")

@router.post("/", response_model=Saree, status_code=201)
async def create_saree(saree: Saree):
    for existing in fake_saree_db:
        if existing.id == saree.id:
            raise HTTPException(status_code=400, detail="Saree ID already exists")
    fake_saree_db.append(saree)
    return saree
