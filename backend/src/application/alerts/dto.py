from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AlertDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    location_id: UUID | None = None
    zone_id: UUID | None = None
    device_id: UUID | None = None
    severity: str
    message: str
    event_type: str
    status: str
    created_at: datetime
    # acknowledged_at is intentionally NOT exposed in this phase.
