from uuid import UUID

from sqlalchemy.orm import Session

from domain.actuators.state import ActuatorState
from domain.events.bus import EventBus
from domain.events.events import ActuatorStateChanged
from infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)
from infrastructure.persistence.models import DeviceRow


class ActuatorTransitionService:
    def __init__(self, db: Session, bus: EventBus | None = None) -> None:
        self._db = db
        self._states = ActuatorStateRepository(db)
        self._bus = bus or EventBus()

    def transition(
        self,
        device_id: UUID,
        target: str,
    ) -> tuple[ActuatorState, list[str]]:
        snapshot = self._states.get_snapshot(device_id)
        previous = snapshot[0] if snapshot else ActuatorState.IDLE.value

        # Raises LookupError / ValueError / IllegalTransitionError as before.
        state, allowed = self._states.transition(device_id, target)

        device = self._db.get(DeviceRow, device_id)
        self._bus.publish(
            ActuatorStateChanged(
                device_id=device_id,
                location_id=device.location_id if device else None,
                zone_id=device.zone_id if device else None,
                previous_state=previous,
                state=state.value,
            )
        )

        return state, allowed
