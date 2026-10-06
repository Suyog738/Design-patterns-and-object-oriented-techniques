from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.sensors.reading import Reading
from infrastructure.persistence.models import ReadingRow


class ReadingRepository:
    def __init__(self, db: Session):
        self._db = db

    def insert(self, reading: Reading) -> Reading:
        row = ReadingRow(
            device_id=reading.device_id,
            value=reading.value,
            unit=reading.unit,
            source=reading.source,
            recorded_at=reading.recorded_at,
        )

        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)

        return Reading(
            device_id=row.device_id,
            value=float(row.value),
            unit=row.unit,
            source=row.source,
            recorded_at=row.recorded_at,
        )

    def list_for_device(
        self,
        device_id: UUID,
        limit: int = 20,
    ) -> list[Reading]:

        statement = (
            select(ReadingRow)
            .where(ReadingRow.device_id == device_id)
            .order_by(ReadingRow.recorded_at.desc())
            .limit(limit)
        )

        rows = self._db.scalars(statement).all()

        return [
            Reading(
                device_id=row.device_id,
                value=float(row.value),
                unit=row.unit,
                source=row.source,
                recorded_at=row.recorded_at,
            )
            for row in rows
        ]