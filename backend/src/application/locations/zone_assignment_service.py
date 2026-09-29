from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.persistence.models import DeviceRow, ZoneRow


class ZoneAssignmentService:
    def __init__(self, db: Session):
        self._db = db

    def assign(
        self,
        device_id: UUID,
        zone_id: UUID | None,
    ) -> None:
        device = self._db.get(DeviceRow, device_id)

        if device is None:
            raise ValueError("Device not found.")

        if zone_id is None:
            device.zone_id = None
            device.location_id = None
            self._db.commit()
            return

        zone = self._db.get(ZoneRow, zone_id)

        if zone is None:
            raise ValueError("Zone not found.")

        device.zone_id = zone.id
        device.location_id = zone.location_id

        self._db.commit()

    def list_devices(
        self,
        location_id: UUID,
        zone_id: UUID,
    ) -> list[DeviceRow]:
        zone = self._db.get(ZoneRow, zone_id)

        if zone is None:
            raise ValueError("Zone not found.")

        if zone.location_id != location_id:
            raise ValueError("Zone does not belong to this location.")

        statement = (
            select(DeviceRow)
            .where(
                DeviceRow.zone_id == zone_id,
                DeviceRow.location_id == location_id,
            )
            .order_by(DeviceRow.created_at)
        )

        return list(self._db.scalars(statement).all())