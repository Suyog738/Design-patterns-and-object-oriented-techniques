from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.persistence.models import ActuatorExecutionLogRow


class ActuatorExecutionLogRepository:
    def __init__(self, db: Session):
        self._db = db

    def add(
        self,
        device_id: UUID,
        success: bool,
        policy_applied: list[str],
        message: str | None,
    ) -> ActuatorExecutionLogRow:
        row = ActuatorExecutionLogRow(
            device_id=device_id,
            success=success,
            policy_applied=policy_applied,
            message=message,
        )

        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)

        return row

    def list_recent(
        self,
        limit: int = 20,
    ) -> list[ActuatorExecutionLogRow]:
        statement = (
            select(ActuatorExecutionLogRow)
            .order_by(ActuatorExecutionLogRow.created_at.desc())
            .limit(limit)
        )

        return list(self._db.scalars(statement).all())
