import hashlib
import urllib.request
from infra.database import Database
from infra.ports.extractor import Extractor
from infra.ports.splitter import Splitter


class KnowledgeService:
    db: Database
    splitter: Splitter
    extractors: list[Extractor]

    def __init__(self, db: Database, splitter: Splitter, extractors: list[Extractor]) -> None:
        self.db = db
        self.splitter = splitter
        self.extractors = extractors

    def fetch_and_apply(self, urls: list[str]) -> None:
        for url in urls:
            content: str = ""
            try:
                content = self._fetch(url)
            except Exception:
                extractor = self.pick_extractor(url)
                content = extractor.extract(url)

            chunks = self.splitter.split_text(content)
            documents, ids = [], []
            for chunk in chunks:
                documents.append(chunk)
                ids.append(hashlib.md5(chunk.encode()).hexdigest())

            self.apply_many(documents, ids)

    def pick_extractor(self, url: str) -> Extractor:
        if url.endswith(".pdf"):
            for extractor in self.extractors:
                if extractor.extension == ".pdf":
                    return extractor
                
        raise ValueError(f"No suitable extractor found for URL: {url}")

    def apply(self, content: str) -> None:
        self.db.collection.add(
            documents=[content],
            ids=[str(hash(content))],
        )

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
    
    def _fetch(self, url: str) -> str:
        with urllib.request.urlopen(url) as response:
            return response.read().decode("utf-8")