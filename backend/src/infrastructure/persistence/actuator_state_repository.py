from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.actuators.context import ActuatorContext
from domain.actuators.state import (
    ActuatorState,
    IllegalTransitionError,
)
from infrastructure.persistence.models import ActuatorStateRow, DeviceRow
from datetime import datetime


class ActuatorStateRepository:
    def __init__(self, db: Session):
        self._db = db

    def get_states(
        self,
        device_ids: list[UUID],
    ) -> dict[UUID, str]:
        if not device_ids:
            return {}

        statement = select(ActuatorStateRow).where(
            ActuatorStateRow.device_id.in_(device_ids)
        )
        rows = self._db.scalars(statement).all()

        return {
            row.device_id: row.state
            for row in rows
        }
    
    def get_snapshot(
        self,
        device_id: UUID,
    ) -> tuple[str, datetime] | None:
        row = self._db.get(ActuatorStateRow, device_id)

        if row is None:
            return None

        return row.state, row.updated_at

    def transition(
        self,
        device_id: UUID,
        target: str,
    ) -> tuple[ActuatorState, list[str]]:
        device = self._db.get(DeviceRow, device_id)

        if device is None:
            raise LookupError("Device not found.")

        if device.role != "actuator":
            raise ValueError("State transitions are only available for actuators.")

        state_row = self._db.get(ActuatorStateRow, device_id)

        if state_row is None:
            state_row = ActuatorStateRow(
                device_id=device_id,
                state=ActuatorState.IDLE.value,
            )
            self._db.add(state_row)
            self._db.flush()

        context = ActuatorContext(ActuatorState(state_row.state))
        context.transition(target)

        state_row.state = context.state.value

        self._db.commit()
        self._db.refresh(state_row)

        return context.state, context.allowed_commands()