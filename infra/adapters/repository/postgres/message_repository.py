from datetime import timezone

from domain.entities.message import Message
from domain.repositories.message_repository import MessageRepository
from infra.ports.database import Database


class PostgresMessageRepository(MessageRepository):

    def __init__(self, db: Database) -> None:
        self.db = db

    def save(self, message: Message) -> None:
        self.db.execute(
            "INSERT INTO messages (id, message_from, content, model) VALUES (%s, %s, %s, %s)",
            (str(message.id), message.from_field, message.content, message.model),
        )

    def list_recent(self, limit: int = 50) -> list[Message]:
        rows = self.db.execute(
            "SELECT id, message_from, content, created_at, model FROM messages ORDER BY created_at DESC LIMIT %s",
            (limit,),
        )
        return [
            Message(
                id=row["id"],
                from_field=row["message_from"],
                content=row["content"],
                created_at=row["created_at"].replace(tzinfo=timezone.utc),
                model=row.get("model"),
            )
            for row in rows
        ]
