import hashlib
import os
from infra.database import ChromaDatabase
from infra.ports.reranker import Reranker
from infra.ports.splitter import Splitter
from services.extractor import ExtractorService


class KnowledgeService:
    db: ChromaDatabase
    splitter: Splitter
    extractor_service: ExtractorService
    reranker: Reranker | None

    def __init__(
        self,
        db: ChromaDatabase,
        splitter: Splitter,
        extractor_service: ExtractorService,
        reranker: Reranker | None = None,
    ) -> None:
        self.db = db
        self.splitter = splitter
        self.extractor_service = extractor_service
        self.reranker = reranker
        self._reranker_enabled = os.getenv("RERANKER_ENABLED", "false").lower() == "true"
        self._initial_results = int(os.getenv("RERANKER_INITIAL_RESULTS", "10"))
        self._final_results = int(os.getenv("RERANKER_FINAL_RESULTS", "3"))

    def fetch_and_apply(self, urls: list[str]) -> None:
        for url in urls:
            content = self.extractor_service.extract(url)
            chunks = self.splitter.split_text(content)
            documents, ids = [], []
            for chunk in chunks:
                documents.append(chunk)
                ids.append(hashlib.md5(chunk.encode()).hexdigest())

            self.apply_many(documents, ids)

    def apply(self, content: str) -> None:
        self.db.collection.add(
            documents=[content],
            ids=[str(hash(content))],
        )

    def ingest_content(self, content: str) -> int:
        chunks = self.splitter.split_text(content)
        documents, ids = [], []
        for chunk in chunks:
            documents.append(chunk)
            ids.append(hashlib.md5(chunk.encode()).hexdigest())
        self.apply_many(documents, ids)
        return len(documents)

    def apply_many(self, contents: list[str], ids: list[str]) -> None:
        self.db.collection.add(
            documents=contents,
            ids=ids,
        )

    def query(self, query: str) -> list[str]:
        if self._reranker_enabled and self.reranker is not None:
            results = self.db.collection.query(
                query_texts=[query],
                n_results=self._initial_results,
            )
            documents = results["documents"][0]
            return self.reranker.rerank(query, documents, self._final_results)
        else:
            results = self.db.collection.query(
                query_texts=[query],
                n_results=3,
            )
            return results["documents"][0]