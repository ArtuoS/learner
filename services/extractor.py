import urllib

from infra.ports.extractor import Extractor


class ExtractorService:
    def __init__(self, extractors: list[Extractor]) -> None:
        self.extractors = extractors

    def extract(self, content: str) -> str:
        converted_content: str = ""
        try:
            converted_content = self._fetch(content)
        except Exception:
            extractor = self.pick_extractor(content)
            converted_content = extractor.extract(content)

        return converted_content

    def pick_extractor(self, url: str) -> Extractor:
        suffix = f".{url.split('.')[-1]}"
        for extractor in self.extractors:
            if extractor.extension == suffix:
                return extractor

        raise ValueError(f"No suitable extractor found for URL: {url}")

    def _fetch(self, url: str) -> str:
        with urllib.request.urlopen(url) as response:
            return response.read().decode("utf-8")
