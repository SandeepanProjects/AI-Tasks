from abc import ABC
from abc import abstractmethod


class VectorStore(ABC):

    @abstractmethod
    async def search(
        self,
        query_vector,
        top_k: int
    ):
        pass


    @abstractmethod
    async def upsert(
        self,
        ids,
        vectors,
        payloads
    ):
        pass