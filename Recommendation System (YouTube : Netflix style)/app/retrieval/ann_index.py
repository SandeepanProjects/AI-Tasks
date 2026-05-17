import faiss
import numpy as np


class ANNIndex:

    def __init__(self, dim=64):
        self.index = faiss.IndexHNSWFlat(dim, 32)

    def build(self, embeddings: np.ndarray):
        self.index.add(embeddings)

    def search(self, query_embedding, top_k=100):

        distances, indices = self.index.search(
            query_embedding,
            top_k
        )

        return indices[0]