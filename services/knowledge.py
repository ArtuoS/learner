import hashlib
from infra.database import Database
from infra.ports.extractor import Extractor
from infra.ports.splitter import Splitter
from services.extractor import ExtractorService


class KnowledgeService:
    db: Database
    splitter: Splitter
    extractor_service: ExtractorService

    def __init__(self, db: Database, splitter: Splitter, extractor_service: ExtractorService) -> None:
        self.db = db
        self.splitter = splitter
        self.extractor_service = extractor_service

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
        results = self.db.collection.query(
            query_texts=[query],
            n_results=3
        )
        return results["documents"][0]