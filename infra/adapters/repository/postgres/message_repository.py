from datetime import timezone
from uuid import UUID

from domain.entities.message import Message
from domain.repositories.message_repository import MessageRepository
from infra.ports.database import Database


class PostgresMessageRepository(MessageRepository):

    def __init__(self, db: Database) -> None:
        self.db = db

    def save(self, message: Message) -> None:
        self.db.execute(
            "INSERT INTO messages (id, message_from, content, tenant_id, session_id, model) VALUES (%s, %s, %s, %s, %s, %s)",
            (str(message.id), message.from_field, message.content, str(message.tenant_id), str(message.session_id) if message.session_id else None, message.model),
        )

    def list_recent(self, limit: int = 50) -> list[Message]:
        rows = self.db.execute(
            "SELECT id, message_from, content, tenant_id, session_id, created_at, model FROM messages ORDER BY created_at DESC LIMIT %s",
            (limit,),
        )
        return [
            Message(
                id=row["id"],
                from_field=row["message_from"],
                content=row["content"],
                tenant_id=row["tenant_id"],
                session_id=row.get("session_id"),
                created_at=row["created_at"].replace(tzinfo=timezone.utc),
                model=row.get("model"),
            )
            for row in rows
        ]

    def list_by_session(self, session_id: UUID, tenant_id: UUID) -> list[Message]:
        rows = self.db.execute(
            "SELECT id, message_from, content, tenant_id, session_id, created_at, model FROM messages WHERE session_id = %s AND tenant_id = %s ORDER BY created_at ASC",
            (str(session_id), str(tenant_id)),
        )
        return [
            Message(
                id=row["id"],
                from_field=row["message_from"],
                content=row["content"],
                tenant_id=row["tenant_id"],
                session_id=row.get("session_id"),
                created_at=row["created_at"].replace(tzinfo=timezone.utc),
                model=row.get("model"),
            )
            for row in rows
        ]
