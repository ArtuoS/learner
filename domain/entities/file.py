from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class File:
    name: str
    tenant_id: UUID
    size: int
    created_at: datetime = field(default_factory=datetime.now)
    id: UUID = field(default_factory=uuid4)
