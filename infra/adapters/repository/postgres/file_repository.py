from datetime import timezone
from uuid import UUID

from domain.entities.file import File
from domain.repositories.file_repository import FileRepository
from infra.ports.database import Database


class PostgresFileRepository(FileRepository):

    def __init__(self, db: Database) -> None:
        self.db = db

    def save(self, file: File) -> None:
        self.db.execute(
            "INSERT INTO files (id, name, tenant_id, size) VALUES (%s, %s, %s, %s)",
            (str(file.id), file.name, str(file.tenant_id), file.size),
        )

    def list_by_tenant(self, tenant_id: UUID, limit: int = 50) -> list[File]:
        rows = self.db.execute(
            "SELECT id, name, tenant_id, size, created_at FROM files WHERE tenant_id = %s ORDER BY created_at DESC LIMIT %s",
            (str(tenant_id), limit),
        )
        return [
            File(
                id=row["id"],
                name=row["name"],
                tenant_id=row["tenant_id"],
                size=row["size"],
                created_at=row["created_at"].replace(tzinfo=timezone.utc),
            )
            for row in rows
        ]
