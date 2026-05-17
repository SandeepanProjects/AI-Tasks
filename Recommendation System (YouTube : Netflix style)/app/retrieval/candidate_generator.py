import numpy as np
from app.retrieval.ann_index import ANNIndex


class CandidateGenerator:

    def __init__(self):

        self.index = ANNIndex()

        embeddings = np.random.rand(10000, 64).astype("float32")

        self.index.build(embeddings)

    def generate(self, user_embedding):

        user_embedding = np.array(
            [user_embedding],
            dtype="float32"
        )
        return self.index.search(user_embedding)