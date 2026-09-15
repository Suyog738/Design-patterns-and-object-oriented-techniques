from dataclasses import dataclass
from uuid import UUID


@dataclass
class Sensor:
    id: UUID | None
    device_type: str
    display_name: str | None
    default_config: dict