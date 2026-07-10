from langchain_text_splitters import RecursiveCharacterTextSplitter

from infra.ports.splitter import Splitter


class LangChainSplitter(Splitter):
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )

    def split_text(self, text: str) -> list[str]:
        return self.text_splitter.split_text(text)
