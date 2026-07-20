from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.message import Message


class MessageRepository(ABC):

    @abstractmethod
    def save(self, message: Message) -> None:
        pass

    @abstractmethod
    def list_recent(self, limit: int = 50) -> list[Message]:
        pass

    @abstractmethod
    def list_by_session(self, session_id: UUID, tenant_id: UUID) -> list[Message]:
        pass
