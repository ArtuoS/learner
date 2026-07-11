from abc import ABC, abstractmethod


class Reranker(ABC):

    @abstractmethod
    def rerank(self, query: str, documents: list[str], top_k: int) -> list[str]:
        pass