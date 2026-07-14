from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator


class Model(ABC):

    @abstractmethod
    def ask(self, instructions: str, context: str, question: str) -> str:
        pass

    @abstractmethod
    async def ask_stream(self, instructions: str, context: str, question: str) -> AsyncGenerator[str, None]:
        pass