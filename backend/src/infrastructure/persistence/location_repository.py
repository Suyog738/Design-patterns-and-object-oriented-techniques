from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.locations.entity import LocationConfig
from infrastructure.persistence.models import LocationRow, ZoneRow


class LocationRepository:
    def __init__(self, db: Session):
        self._db = db

    def save_config(
        self,
        config: LocationConfig,
    ) -> tuple[LocationRow, list[ZoneRow]]:
        location_row = LocationRow(
            name=config.location.name,
        )

        self._db.add(location_row)

        # Get the generated location UUID before creating zones.
        self._db.flush()

        zone_rows = [
            ZoneRow(
                location_id=location_row.id,
                name=zone.name,
                moisture_threshold_low=zone.moisture_threshold_low,
                moisture_threshold_high=zone.moisture_threshold_high,
                schedule=zone.schedule,
            )
            for zone in config.zones
        ]

        self._db.add_all(zone_rows)

        # Save location and all zones together.
        self._db.commit()

        self._db.refresh(location_row)

        for zone_row in zone_rows:
            self._db.refresh(zone_row)

        return location_row, zone_rows

    def get_config(
        self,
        location_id: UUID,
    ) -> tuple[LocationRow, list[ZoneRow]] | None:
        location_row = self._db.get(LocationRow, location_id)

        if location_row is None:
            return None

        statement = (
            select(ZoneRow)
            .where(ZoneRow.location_id == location_id)
            .order_by(ZoneRow.name)
        )

        zone_rows = list(self._db.scalars(statement).all())

        return location_row, zone_rows