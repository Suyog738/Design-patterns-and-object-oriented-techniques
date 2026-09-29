from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True)
class Zone:
    id: UUID | None
    name: str
    moisture_threshold_low: float
    moisture_threshold_high: float
    schedule: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Location:
    id: UUID | None
    name: str


@dataclass(frozen=True)
class LocationConfig:
    location: Location
    zones: tuple[Zone, ...]