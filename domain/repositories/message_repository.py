from abc import ABC, abstractmethod

from domain.entities.message import Message


class MessageRepository(ABC):

    @abstractmethod
    def save(self, message: Message) -> None:
        pass

    @abstractmethod
    def list_recent(self, limit: int = 50) -> list[Message]:
        pass
