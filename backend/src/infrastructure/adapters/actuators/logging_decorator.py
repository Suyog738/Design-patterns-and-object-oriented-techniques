from uuid import UUID

from domain.actuators.ports import ActuatorPolicyError, ActuatorPort
from infrastructure.persistence.execution_log_repository import (
    ActuatorExecutionLogRepository,
)


class LoggingActuatorDecorator(ActuatorPort):
    POLICY = "logging"

    def __init__(
        self,
        inner: ActuatorPort,
        log_repo: ActuatorExecutionLogRepository,
    ) -> None:
        self._inner = inner
        self._log_repo = log_repo

    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict,
    ) -> None:
        try:
            self._inner.apply(device_id, command, payload)
        except ActuatorPolicyError as exc:
            self._log_repo.add(
                device_id=device_id,
                success=False,
                policy_applied=[exc.policy, self.POLICY],
                message=str(exc),
            )
            raise
        except Exception as exc:
            self._log_repo.add(
                device_id=device_id,
                success=False,
                policy_applied=[self.POLICY],
                message=str(exc),
            )
            raise

        self._log_repo.add(
            device_id=device_id,
            success=True,
            policy_applied=[self.POLICY],
            message=None,
        )
