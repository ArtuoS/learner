from abc import ABC, abstractmethod


class Splitter(ABC):
    
    @abstractmethod
    def split_text(self, text: str) -> list[str]:
        pass