from urllib.request import urlopen

from infra.ports.extractor import Extractor

class TXTExtractor(Extractor):
    def __init__(self):
        self.extension = ".txt"

    def extract(self, source: str) -> str:
        if self.is_url(source):
            with urlopen(source) as response:
                return response.read().decode('utf-8')
        
        with open(source, 'r', encoding='utf-8') as file:
            return file.read()

    def is_url(self, source: str) -> bool:
        return source.startswith(("http://", "https://"))