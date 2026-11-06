from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from uuid import UUID

from domain.actuators.ports import ActuatorPolicyError, ActuatorPort
from domain.actuators.state import ActuatorState
from infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)


class MaxRunTimeActuatorDecorator(ActuatorPort):
    POLICY = "maxRunTime"

    def __init__(
        self,
        inner: ActuatorPort,
        state_repo: ActuatorStateRepository,
        max_run_time: timedelta = timedelta(minutes=30),
        clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    ) -> None:
        self._inner = inner
        self._state_repo = state_repo
        self._max_run_time = max_run_time
        self._clock = clock

    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict,
    ) -> None:
        snapshot = self._state_repo.get_snapshot(device_id)

        if snapshot is not None:
            state, updated_at = snapshot

            if (
                state == ActuatorState.RUNNING.value
                and self._clock() - updated_at >= self._max_run_time
            ):
                # Blocked: the inner port is never called.
                raise ActuatorPolicyError(
                    self.POLICY,
                    "Max run time exceeded",
                )

        self._inner.apply(device_id, command, payload)
