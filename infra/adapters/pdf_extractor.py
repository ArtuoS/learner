import io
from urllib.request import urlopen

from pypdf import PdfReader

from infra.ports.extractor import Extractor


class PDFExtractor(Extractor):
    def __init__(self):
        self.extension = ".pdf"

    def extract(self, source: str) -> str:
        if self.is_url(source):
            with urlopen(source) as response:
                pdf_bytes = response.read()

            reader = PdfReader(io.BytesIO(pdf_bytes))
        else:
            reader = PdfReader(source)

        text = ""
        for _, page in enumerate(reader.pages):
            page_text = page.extract_text()
            text += page_text
        return text

    def is_url(self, source: str) -> bool:
        return source.startswith(("http://", "https://"))
