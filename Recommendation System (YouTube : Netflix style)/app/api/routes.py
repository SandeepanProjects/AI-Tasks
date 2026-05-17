from fastapi import APIRouter
import numpy as np

from app.retrieval.candidate_generator import CandidateGenerator
from app.ranking.features import build_features
from app.ranking.ranker import Ranker
from app.reranking.diversity import DiversityReranker
from app.cache.redis_cache import (
    cache_recommendations,
    get_cached_recommendations
)


router = APIRouter()

candidate_generator = CandidateGenerator()
ranker = Ranker()
diversity = DiversityReranker()

@router.get("/recommend/{user_id}")
async def recommend(user_id: str):

    cached = get_cached_recommendations(user_id)

    if cached:
        return {
            "source": "cache",
            "recommendations": cached
        }

    user_embedding = np.random.rand(64)

    candidates = candidate_generator.generate(
        user_embedding
    )

    features = build_features(
        user_id,
        candidates
    )
    
    ranked = ranker.rank(
        features,
        candidates
    )

    reranked = diversity.rerank(ranked)

    recommendations = reranked[:20]

    cache_recommendations(
        user_id,
        recommendations
    )

    return {
        "source": "model",
        "recommendations": recommendations
    }