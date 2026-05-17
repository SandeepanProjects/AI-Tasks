from pydantic import BaseModel
from typing import List


class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[int]