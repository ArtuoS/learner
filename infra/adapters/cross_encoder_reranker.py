import os
from sentence_transformers import CrossEncoder

from infra.ports.reranker import Reranker


class CrossEncoderReranker(Reranker):
    _model: CrossEncoder | None = None

    def __init__(self) -> None:
        self.model = CrossEncoder(os.getenv(
            "RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2"
        ))

    def rerank(self, query: str, documents: list[str], top_k: int) -> list[str]:
        if not documents:
            return []

        pairs = [(query, doc) for doc in documents]
        scores = self.model.predict(pairs)

        scored_docs = list(zip(documents, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        return [doc for doc, _ in scored_docs[:top_k]]
