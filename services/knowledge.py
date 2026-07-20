import hashlib
import os
from uuid import UUID

from infra.database import ChromaDatabase
from infra.ports.reranker import Reranker
from infra.ports.splitter import Splitter


class KnowledgeService:
    db: ChromaDatabase
    splitter: Splitter
    reranker: Reranker | None

    def __init__(
        self,
        db: ChromaDatabase,
        splitter: Splitter,
        reranker: Reranker | None = None,
    ) -> None:
        self.db = db
        self.splitter = splitter
        self.reranker = reranker
        self._reranker_enabled = os.getenv("RERANKER_ENABLED", "false").lower() == "true"
        self._initial_results = int(os.getenv("RERANKER_INITIAL_RESULTS", "10"))
        self._final_results = int(os.getenv("RERANKER_FINAL_RESULTS", "3"))

    def apply(self, content: str, tenant_id: UUID) -> None:
        self.db.collection.add(
            documents=[content],
            ids=[self._get_document_id(content, tenant_id)],
            metadatas=[{"tenant_id": str(tenant_id)}],
        )

    def ingest_content(self, content: str, tenant_id: UUID) -> int:
        chunks = self.splitter.split_text(content)
        documents, ids = [], []
        for chunk in chunks:
            documents.append(chunk)
            ids.append(self._get_document_id(chunk, tenant_id))
        self.apply_many(documents, ids, tenant_id)
        return len(documents)

    def apply_many(self, contents: list[str], ids: list[str], tenant_id: UUID) -> None:
        self.db.collection.add(
            documents=contents,
            ids=ids,
            metadatas=[{"tenant_id": str(tenant_id)}] * len(contents),
        )

    def query(self, query: str, tenant_id: UUID) -> list[str]:
        if self._reranker_enabled and self.reranker is not None:
            results = self.db.collection.query(
                query_texts=[query],
                n_results=self._initial_results,
                where={"tenant_id": str(tenant_id)},
            )
            documents = results["documents"][0]
            return self.reranker.rerank(query, documents, self._final_results)
        else:
            results = self.db.collection.query(
                query_texts=[query],
                n_results=3,
                where={"tenant_id": str(tenant_id)},
            )
            return results["documents"][0]

    def _get_document_id(self, content: str, tenant_id: UUID) -> str:
        return f"{hashlib.md5(content.encode()).hexdigest()}_{tenant_id}"