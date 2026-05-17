Recommendation System (YouTube / Netflix style)

A production-grade recommendation system like YouTube or Netflix is not just “train a model and recommend items.”
It is a distributed ML platform involving:

* Candidate generation
* Retrieval
* Ranking
* Re-ranking
* Feature stores
* Real-time streaming
* Feedback loops
* Exploration vs exploitation
* Online inference
* A/B testing
* Monitoring
* Cold-start handling
* Abuse prevention
* Diversity/freshness logic

Below is a senior-level architecture + production-grade Python implementation structure.

---

# 1. High-Level System Design

## Multi-Stage Recommendation Pipeline

```text
                    ┌─────────────────┐
                    │ User Events     │
                    │ clicks/views    │
                    └────────┬────────┘
                             │
                             ▼
                 ┌────────────────────┐
                 │ Kafka / Streaming  │
                 └────────┬───────────┘
                          │
          ┌───────────────┴────────────────┐
          ▼                                ▼
 ┌─────────────────┐              ┌─────────────────┐
 │ Feature Store   │              │ Real-time Stats │
 │ Redis/Feast     │              │ CTR/watch time  │
 └────────┬────────┘              └────────┬────────┘
          │                                │
          └───────────────┬────────────────┘
                          ▼
                ┌──────────────────┐
                │ Candidate Gen    │
                │ ANN Retrieval    │
                └────────┬─────────┘
                         ▼
                ┌──────────────────┐
                │ Ranking Model    │
                │ XGBoost/DLRM     │
                └────────┬─────────┘
                         ▼
                ┌──────────────────┐
                │ Re-ranking       │
                │ Diversity/Fresh  │
                └────────┬─────────┘
                         ▼
                ┌──────────────────┐
                │ API Service      │
                │ FastAPI/gRPC     │
                └──────────────────┘
```

---

# 2. Production Folder Structure

---

# 3. Recommendation System Architecture

## Stage 1 — Candidate Generation

Goal:

```text
Millions of videos
      ↓
few hundred candidates
```

Techniques:

| Technique               | Example                            |
| ----------------------- | ---------------------------------- |
| Collaborative filtering | users who watched X also watched Y |
| Embeddings              | vector similarity                  |
| Trending retrieval      | trending now                       |
| Graph retrieval         | co-watch graph                     |
| Personalized ANN search | nearest embeddings                 |

---

# 4. Candidate Retrieval (ANN Search)

## Why ANN?

Brute force:

```text
10M videos × 512 dims = impossible online
```

Use:

* FAISS
* ScaNN
* HNSW
* Milvus
* Pinecone
* Weaviate

---

# 5. Production Embedding Training

## Two-Tower Architecture

Used heavily at YouTube.

```text
User Tower                    Item Tower
-----------                  -----------
watch history                title
searches                     tags
likes                        category
language                     creator
device                       embedding

        cosine similarity
```

---

# 6. Embedding Training Code

```python
# app/training/train_embeddings.py

import torch
import torch.nn as nn

class UserTower(nn.Module):
    def __init__(self, input_dim=128, emb_dim=64):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(0.2),

            nn.Linear(256, emb_dim)
        )

    def forward(self, x):
        return self.network(x)


class ItemTower(nn.Module):
    def __init__(self, input_dim=128, emb_dim=64):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(0.2),

            nn.Linear(256, emb_dim)
        )

    def forward(self, x):
        return self.network(x)


class TwoTowerModel(nn.Module):
    def __init__(self):
        super().__init__()

        self.user_tower = UserTower()
        self.item_tower = ItemTower()

    def forward(self, user_features, item_features):
        user_emb = self.user_tower(user_features)
        item_emb = self.item_tower(item_features)

        similarity = torch.sum(user_emb * item_emb, dim=1)

        return similarity
```

---

# 7. ANN Vector Index (FAISS)

```python
# app/retrieval/ann_index.py

import faiss
import numpy as np

class ANNIndex:

    def __init__(self, dim=64):
        self.index = faiss.IndexHNSWFlat(dim, 32)

    def build(self, embeddings: np.ndarray):
        self.index.add(embeddings)

    def search(self, query_vector, top_k=50):
        distances, indices = self.index.search(
            query_vector,
            top_k
        )

        return indices[0]
```

---

# 8. Retrieval Service

```python
# app/retrieval/candidate_generator.py

class CandidateGenerator:

    def __init__(self, ann_index, embedding_model):
        self.ann_index = ann_index
        self.embedding_model = embedding_model

    def generate_candidates(self, user_features):

        user_embedding = self.embedding_model.encode_user(
            user_features
        )

        candidates = self.ann_index.search(
            user_embedding,
            top_k=500
        )

        return candidates
```

---

# 9. Ranking System

Retrieval gives:

```text
500 candidates
```

Ranking model sorts them precisely.

---

# 10. Ranking Features

## User Features

* age bucket
* region
* watch history
* watch duration
* active hours

## Item Features

* video age
* CTR
* creator quality
* category
* embeddings

## Context Features

* time of day
* device
* network speed
* session length

---

# 11. Ranking Model

Usually:

| Scale      | Model                     |
| ---------- | ------------------------- |
| Small      | XGBoost                   |
| Medium     | LightGBM                  |
| Large      | DLRM                      |
| Very large | Deep ranking transformers |

---

# 12. XGBoost Ranker

```python
# app/ranking/train_ranker.py

import xgboost as xgb

class RankingModel:

    def __init__(self):

        self.model = xgb.XGBRanker(
            tree_method="hist",
            objective="rank:pairwise",
            max_depth=8,
            learning_rate=0.05,
            n_estimators=300,
            subsample=0.8,
            colsample_bytree=0.8
        )

    def train(self, X, y, group):

        self.model.fit(
            X,
            y,
            group=group
        )

    def predict(self, X):
        return self.model.predict(X)
```

---

# 13. Re-ranking Layer

Critical in production.

Without re-ranking:

```text
10 identical comedy videos
```

Bad UX.

---

# 14. Re-ranking Objectives

## Diversity

Avoid repetitive content.

## Freshness

Inject recent uploads.

## Serendipity

Show unexpected but useful content.

## Business Rules

* no banned videos
* no NSFW
* regional restrictions
* ads insertion

---

# 15. Diversity Re-ranker

```python
class DiversityReranker:

    def rerank(self, ranked_items):

        seen_categories = set()
        results = []

        for item in ranked_items:

            if item.category not in seen_categories:
                results.append(item)
                seen_categories.add(item.category)

        return results
```

---

# 16. Cold Start Problem

One of the hardest production issues.

---

# 17. New User Cold Start

No history.

Solutions:

* onboarding interests
* trending recommendations
* demographic priors
* contextual bandits
* session-based recommendations

---

# 18. New Item Cold Start

No interactions.

Solutions:

* content embeddings
* creator similarity
* metadata models
* exploration traffic

---

# 19. Exploration vs Exploitation

Massive production topic.

---

# 20. Multi-Armed Bandits

Avoid overfitting recommendations.

Popular methods:

* Thompson Sampling
* UCB
* Contextual bandits

---

# 21. Real-Time Features

Production systems use:

| Component | Purpose               |
| --------- | --------------------- |
| Kafka     | streaming events      |
| Redis     | online features       |
| Feast     | feature store         |
| Spark     | offline features      |
| Flink     | streaming aggregation |

---

# 22. Real-Time Event Pipeline

```text
user click
    ↓
Kafka
    ↓
stream processor
    ↓
Redis counters
    ↓
online ranking features
```

---

# 23. Feature Store Design

## Offline Store

Training consistency.

## Online Store

Low-latency serving.

Popular:

* Feast
* Tecton

---

# 24. API Service (FastAPI)

```python
# app/api/routes.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/recommend/{user_id}")
async def recommend(user_id: str):

    candidates = retrieval.generate(user_id)

    ranked = ranker.rank(candidates)

    reranked = reranker.apply(ranked)

    return {
        "recommendations": reranked[:20]
    }
```

---

# 25. Caching Strategy

Extremely important.

## Cache Layers

### Embedding Cache

```text
user embeddings
```

### Recommendation Cache

```text
homepage recommendations
```

### Feature Cache

```text
CTR stats
```

---

# 26. Redis Caching

```python
import redis
import json

redis_client = redis.Redis()

def cache_recommendations(user_id, recs):

    redis_client.setex(
        f"recs:{user_id}",
        300,
        json.dumps(recs)
    )
```

---

# 27. Edge Cases (Senior-Level)

# A. User Has No History

Fallback:

```text
trending + onboarding interests
```

---

# B. Sparse Users

Very few interactions.

Use:

* graph retrieval
* popularity priors

---

# C. Viral Content Explosion

Sudden popularity spike.

Need:

* streaming popularity counters
* fast refresh ANN

---

# D. Feedback Loops

System keeps reinforcing same content.

Fix:

* diversity penalties
* exploration traffic

---

# E. Position Bias

Users click top items more.

Fix:

* debiasing models
* inverse propensity scoring

---

# F. Shilling Attacks

Fake engagement.

Fix:

* anomaly detection
* fraud scoring
* trust-weighted interactions

---

# G. Multi-Device Users

Different devices produce different behavior.

Need:

* identity resolution
* session stitching

---

# H. Latency Constraints

Production target:

| Stage     | Target |
| --------- | ------ |
| Retrieval | <50ms  |
| Ranking   | <100ms |
| Total     | <200ms |

---

# 28. Monitoring

Critical in production.

---

# 29. What To Monitor

## System Metrics

* latency
* CPU
* GPU
* memory

## ML Metrics

* CTR
* watch time
* retention
* diversity
* novelty

## Drift Metrics

* embedding drift
* feature drift
* popularity skew

---

# 30. Online Evaluation

## A/B Testing

Never deploy blindly.

Metrics:

* CTR
* session duration
* retention
* revenue
* watch hours

---

# 31. Production Infrastructure

Typical stack:

| Layer      | Tech               |
| ---------- | ------------------ |
| API        | FastAPI/gRPC       |
| ANN        | FAISS/Milvus       |
| Queue      | Kafka              |
| Cache      | Redis              |
| Training   | PyTorch            |
| Ranking    | XGBoost            |
| Serving    | Kubernetes         |
| Monitoring | Prometheus/Grafana |

---

# 32. Advanced Production Enhancements

# A. Session-Based Transformers

Next-item prediction.

---

# B. Graph Neural Networks

User-item graph learning.

---

# C. Sequential Models

* SASRec
* BERT4Rec
* GRU4Rec

---

# D. Reinforcement Learning

Optimize long-term watch time.

---

# 33. Netflix vs YouTube Difference

## Netflix

Focus:

```text
long-term satisfaction
```

Metrics:

* completion rate
* retention

---

## YouTube

Focus:

```text
watch time + ads
```

Requires:

* extreme freshness
* massive scale
* real-time ranking

---

# 34. Production Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recommendation-api

spec:
  replicas: 5

  template:
    spec:
      containers:
      - name: api
        image: recommendation-system:latest

        resources:
          limits:
            cpu: "4"
            memory: "8Gi"
```

---

# 35. Senior-Level Interview Topics

You should be able to explain:

* ANN vs exact search
* HNSW internals
* retrieval vs ranking
* cold start
* feature stores
* online inference
* real-time streaming
* bandits
* exploration
* embedding drift
* A/B testing
* latency optimization
* caching
* sharding
* GPU inference
* model serving

---

# 36. Real Production Companies

| Company | Known Architecture                 |
| ------- | ---------------------------------- |
| YouTube | two-stage deep retrieval + ranking |
| Netflix | personalization + artwork ranking  |
| Spotify | embeddings + audio ML              |
| TikTok  | extreme online learning            |
| Amazon  | retrieval + ranking + ads          |

---

# 37. Most Important Production Insight

The ranking model is often NOT the hardest part.

The hardest parts are:

* data quality
* latency
* feature consistency
* real-time pipelines
* monitoring
* exploration
* abuse prevention
* infrastructure reliability
* online experimentation
* scaling ANN retrieval

Those are what distinguish a senior AI/ML engineer from a beginner.
