import tiktoken

from infra.ports.splitter import Splitter
from langchain_text_splitters import RecursiveCharacterTextSplitter

class LangChainSplitter(Splitter):
    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # encoder = tiktoken.encoding_for_model(os.getenv("OPENAI_MODEL_NAME", "gpt-5-nano"))
        encoder = tiktoken.get_encoding("o200k_base")
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=lambda text: len(encoder.encode(text)),
            separators=["\n\n", "\n", " ", ""]
        )

    def split_text(self, text: str) -> list[str]:
        return self.text_splitter.split_text(text)