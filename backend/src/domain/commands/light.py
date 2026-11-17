from uuid import UUID

from domain.actuators.ports import ActuatorPort
from domain.actuators.state import ActuatorState
from domain.commands.base import Command, InvalidCommandPayloadError


class SetLightLevelCommand(Command):
    command_type = "set_light_level"
    target_state = ActuatorState.RUNNING.value

    def __init__(self, device_id: UUID, payload: dict | None = None) -> None:
        super().__init__(device_id, payload)
        level = self.payload.get("level", 1)

        if isinstance(level, bool) or not isinstance(level, (int, float)):
            raise InvalidCommandPayloadError("level must be a number.")
        if not 0 <= level <= 1:
            raise InvalidCommandPayloadError("level must be between 0 and 1.")

        self.level = float(level)
        self.payload = {**self.payload, "level": self.level}

    def execute(self, port: ActuatorPort) -> None:
        port.apply(self.device_id, self.command_type, {"level": self.level})
