from abc import ABC, abstractmethod
from uuid import UUID

from domain.actuators.ports import ActuatorPort


class UnknownCommandError(ValueError):
    """command_type has no registered Command class (-> 400, no log row)."""


class InvalidCommandPayloadError(ValueError):
    """Payload is malformed for this command (-> 400, no log row)."""


class Command(ABC):
    command_type: str = ""
    # State the actuator should be in after a successful execute; None = no change.
    target_state: str | None = None

    def __init__(self, device_id: UUID, payload: dict | None = None) -> None:
        self.device_id = device_id
        self.payload = dict(payload or {})

    @abstractmethod
    def execute(self, port: ActuatorPort) -> None:
        ...
