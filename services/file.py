from uuid import UUID

from domain.repositories.file_repository import FileRepository


class FileService:

    def __init__(self, file_repo: FileRepository | None = None) -> None:
        self.file_repo = file_repo

    def register(self, filename: str, tenant_id: UUID, size: int) -> None:
        if self.file_repo is None:
            return

        from domain.entities.file import File

        self.file_repo.save(File(name=filename, tenant_id=tenant_id, size=size))
