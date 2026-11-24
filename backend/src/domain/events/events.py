from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class ReadingCreated:
    device_id: UUID
    value: float
    unit: str
    source: str
    recorded_at: datetime
    location_id: UUID | None
    zone_id: UUID | None


@dataclass(frozen=True)
class ThresholdCrossed:
    device_id: UUID
    location_id: UUID | None
    zone_id: UUID | None
    value: float
    threshold: float


@dataclass(frozen=True)
class CommandFailed:
    device_id: UUID
    location_id: UUID | None
    zone_id: UUID | None
    command_type: str
    message: str


@dataclass(frozen=True)
class ActuatorStateChanged:
    device_id: UUID
    location_id: UUID | None
    zone_id: UUID | None
    previous_state: str
    state: str
