from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.persistence.models import CommandLogRow


class CommandLogRepository:
    def __init__(self, db: Session):
        self._db = db

    def add(
        self,
        device_id: UUID,
        command_type: str,
        payload: dict,
        status: str,
        error_message: str | None = None,
    ) -> CommandLogRow:
        row = CommandLogRow(
            device_id=device_id,
            command_type=command_type,
            payload=payload,
            status=status,
            error_message=error_message,
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return row

    def list_recent(self, limit: int = 50) -> list[CommandLogRow]:
        statement = (
            select(CommandLogRow)
            .order_by(CommandLogRow.created_at.desc())
            .limit(limit)
        )
        return list(self._db.scalars(statement).all())
