from uuid import UUID

from domain.actuators.ports import ActuatorPort
from domain.commands.base import Command, UnknownCommandError
from domain.commands.light import SetLightLevelCommand
from domain.commands.pump import StartPumpCommand, StopPumpCommand


COMMAND_REGISTRY: dict[str, type[Command]] = {
    cls.command_type: cls
    for cls in (StartPumpCommand, StopPumpCommand, SetLightLevelCommand)
}


def command_for(command_type: str, device_id: UUID, payload: dict) -> Command:
    try:
        command_class = COMMAND_REGISTRY[command_type]
    except KeyError:
        raise UnknownCommandError(f"Unknown command type: {command_type}") from None

    return command_class(device_id, payload)


class CommandInvoker:
    def run(self, command: Command, port: ActuatorPort) -> None:
        command.execute(port)
