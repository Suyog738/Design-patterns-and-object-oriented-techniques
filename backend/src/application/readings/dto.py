from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ReadingDto(BaseModel):
    device_id: UUID
    value: float
    unit: str
    source: str
    recorded_at: datetime