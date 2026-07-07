from abc import ABC, abstractmethod


class Model(ABC):

    @abstractmethod
    def ask(self, instructions: str, context: str, question: str) -> list[str]:
        pass