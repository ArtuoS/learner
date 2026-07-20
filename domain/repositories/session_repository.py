from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.session import Session


class SessionRepository(ABC):

    @abstractmethod
    def save(self, session: Session) -> None:
        pass

    @abstractmethod
    def find_by_id(self, session_id: UUID) -> Session | None:
        pass

    @abstractmethod
    def list_by_tenant(self, tenant_id: UUID) -> list[Session]:
        pass
