from app.rag.embeddings.embedder import OpenAIEmbedder


class QueryEmbedder:

    def __init__(self):

        self.embedder = OpenAIEmbedder()

    def embed(self, query: str):

        return self.embedder.embed(query)