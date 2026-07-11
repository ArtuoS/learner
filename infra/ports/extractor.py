from abc import ABC, abstractmethod


class Extractor(ABC):
    def __init__(self, extension: str):
        self.extension = extension

    @abstractmethod
    def extract(self, source: str) -> str:
        pass
