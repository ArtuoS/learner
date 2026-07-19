from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Message:
    from_field: str
    content: str
    tenant_id: UUID
    created_at: datetime = field(default_factory=datetime.now)
    model: str | None = None
    id: UUID = field(default_factory=uuid4)
