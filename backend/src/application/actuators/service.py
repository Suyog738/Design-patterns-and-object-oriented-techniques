from uuid import UUID

from sqlalchemy.orm import Session

from application.actuators.dto import ActuatorExecutionDto
from domain.actuators.ports import ActuatorPort
from infrastructure.adapters.actuators.logging_decorator import (
    LoggingActuatorDecorator,
)
from infrastructure.adapters.actuators.max_runtime_decorator import (
    MaxRunTimeActuatorDecorator,
)
from infrastructure.adapters.actuators.simulation import (
    SimulationActuatorAdapter,
)
from infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)
from infrastructure.persistence.execution_log_repository import (
    ActuatorExecutionLogRepository,
)
from infrastructure.persistence.models import DeviceRow


def build_actuator_port(db: Session) -> ActuatorPort:
    # Order: logging -> maxRunTime -> simulation adapter.
    return LoggingActuatorDecorator(
        MaxRunTimeActuatorDecorator(
            SimulationActuatorAdapter(),
            ActuatorStateRepository(db),
        ),
        ActuatorExecutionLogRepository(db),
    )


class ActuatorService:
    def __init__(self, db: Session):
        self._db = db
        self._port = build_actuator_port(db)
        self._log_repository = ActuatorExecutionLogRepository(db)

    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict,
    ) -> None:
        device = self._db.get(DeviceRow, device_id)

        if device is None:
            raise LookupError("Device not found.")

        if device.role != "actuator":
            raise ValueError("Commands are only available for actuators.")

        # Command is not validated here; Phase 10 consults allowed_commands.
        self._port.apply(device_id, command, payload)

    def list_executions(
        self,
        limit: int = 20,
    ) -> list[ActuatorExecutionDto]:
        rows = self._log_repository.list_recent(limit)

        return [
            ActuatorExecutionDto(
                id=row.id,
                device_id=row.device_id,
                success=row.success,
                policy_applied=row.policy_applied,
                message=row.message,
                created_at=row.created_at,
            )
            for row in rows
        ]
