from pypdf import PdfReader

from infra.ports.extractor import Extractor


class PDFExtractor(Extractor):
    def __init__(self):
        pass
    
    def extract(self, source: str) -> str:
        reader = PdfReader(source)
        text = ""
        for _, page in enumerate(reader.pages):
            page_text = page.extract_text()
            text += page_text
        return text