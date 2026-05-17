import numpy as np
from app.ranking.ranker import Ranker

def test_ranker():
    r = Ranker()

    X = np.random.rand(10, 20)
    candidates = list(range(10))

    out = r.rank(X, candidates)

    assert len(out) == len(candidates)