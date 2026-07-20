from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.file import File


class FileRepository(ABC):

    @abstractmethod
    def save(self, file: File) -> None:
        pass

    @abstractmethod
    def list_by_tenant(self, tenant_id: UUID, limit: int = 50) -> list[File]:
        pass
