class Formatter:
    def __init__(self) -> None:
        pass

    def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunks.append(text[i:i + chunk_size])
        return chunks