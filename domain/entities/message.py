from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Message:
    id: UUID = field(default_factory=uuid4)
    from_field: str
    content: str
    created_at: datetime = field(default_factory=datetime.now)
    model: str | None = None
