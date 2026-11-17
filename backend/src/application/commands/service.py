from uuid import UUID

from sqlalchemy.orm import Session

from application.actuators.service import build_actuator_port
from application.commands.dto import CommandLogDto
from domain.actuators.context import ActuatorContext
from domain.actuators.ports import ActuatorPolicyError, ActuatorPort
from domain.actuators.state import ActuatorState
from domain.commands.base import Command
from domain.commands.invoker import CommandInvoker, command_for
from infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)
from infrastructure.persistence.command_log_repository import (
    CommandLogRepository,
)
from infrastructure.persistence.models import DeviceRow


class CommandService:
    def __init__(
        self,
        db: Session,
        port: ActuatorPort | None = None,
        invoker: CommandInvoker | None = None,
    ) -> None:
        self._db = db
        self._port = port or build_actuator_port(db)  # Phase 9 decorated stack
        self._invoker = invoker or CommandInvoker()
        self._logs = CommandLogRepository(db)
        self._states = ActuatorStateRepository(db)

    def submit(
        self,
        command_type: str,
        device_id: UUID,
        payload: dict,
    ) -> CommandLogDto:
        # Unknown type / bad payload raises ValueError -> 400, nothing logged.
        command = command_for(command_type, device_id, payload)

        device = self._db.get(DeviceRow, device_id)
        if device is None:
            raise LookupError("Device not found.")
        if device.role != "actuator":
            raise LookupError("Device is not an actuator.")

        # 1. Guard: no apply, no state write on reject.
        snapshot = self._states.get_snapshot(device_id)
        current = ActuatorState(snapshot[0]) if snapshot else ActuatorState.IDLE
        context = ActuatorContext(current)

        if command.command_type not in context.allowed_commands():
            return self._log(
                command,
                "rejected",
                f"Command {command.command_type} is not allowed "
                f"in state {current.value}.",
            )

        # 2. Port: goes through logging -> maxRunTime -> adapter.
        try:
            self._invoker.run(command, self._port)
        except ActuatorPolicyError as exc:
            # Execution-log row was already written by the decorator.
            return self._log(command, "failed", str(exc))

        # 3. State: only transition when the target differs.
        if (
            command.target_state is not None
            and command.target_state != current.value
        ):
            self._states.transition(device_id, command.target_state)

        # 4. Log success.
        return self._log(command, "success", None)

    def list_recent(self, limit: int = 50) -> list[CommandLogDto]:
        return [
            CommandLogDto.model_validate(row)
            for row in self._logs.list_recent(limit)
        ]

    def _log(
        self,
        command: Command,
        status: str,
        error_message: str | None,
    ) -> CommandLogDto:
        row = self._logs.add(
            device_id=command.device_id,
            command_type=command.command_type,
            payload=command.payload,
            status=status,
            error_message=error_message,
        )
        return CommandLogDto.model_validate(row)
