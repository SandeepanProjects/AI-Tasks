import numpy as np
from app.retrieval.candidate_generator import CandidateGenerator

def test_retrieval():
    cg = CandidateGenerator()

    emb = np.random.rand(64)

    res = cg.generate(emb)

    assert len(res) > 0