from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from application.readings.service import ReadingIngest
from infrastructure.persistence.models import DeviceRow
from infrastructure.persistence.reading_repository import ReadingRepository


class SimulationSampler:
    def __init__(self, db: Session):
        self._db = db
        self._ingest = ReadingIngest(db)
        self._repository = ReadingRepository(db)

    def run_once(self, now: datetime) -> None:
        statement = (
            select(DeviceRow)
            .where(
                DeviceRow.role == "sensor",
                DeviceRow.tracking_enabled.is_(True),
            )
        )

        devices = self._db.scalars(statement).all()

        for device in devices:
            config = device.default_config or {}

            protocol = config.get(
                "protocol",
                "simulation",
            )

            # Sampler only handles simulation sensors.
            if protocol != "simulation":
                continue

            readings = self._repository.list_for_device(
                device.id,
                limit=1,
            )

            if readings:
                last_reading = readings[0]

                elapsed = (
                    now - last_reading.recorded_at
                ).total_seconds()

                if elapsed < device.sampling_interval_seconds:
                    continue

            self._ingest.take_reading(device.id)