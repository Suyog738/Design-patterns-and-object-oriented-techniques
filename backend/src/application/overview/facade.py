
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from application.automation.service import AutomationService
from application.overview.dto import (
    DeviceCountsDto,
    LocationOverviewDto,
    LocationSummaryDto,
    OverviewDeviceDto,
    OverviewReadingDto,
    OverviewRecommendationDto,
    OverviewZoneDto,
)
from infrastructure.persistence.automation_repository import (
    AutomationRepository,
)
from infrastructure.persistence.models import (
    DeviceRow,
    LocationRow,
    ReadingRow,
    ZoneRow,
)


class LocationOverviewFacade:
    def __init__(self, db: Session):
        self._db = db
        self._automation = AutomationService(db)
        self._automation_repository = AutomationRepository(db)

    def get_overview(self, location_id: UUID) -> LocationOverviewDto:
        location = self._db.get(LocationRow, location_id)

        if location is None:
            raise ValueError("Location not found.")

        zones = list(
            self._db.scalars(
                select(ZoneRow)
                .where(ZoneRow.location_id == location_id)
                .order_by(ZoneRow.name)
            ).all()
        )

        devices = list(
            self._db.scalars(
                select(DeviceRow)
                .join(ZoneRow, DeviceRow.zone_id == ZoneRow.id)
                .where(
                    DeviceRow.location_id == location_id,
                    ZoneRow.location_id == location_id,
                )
                .order_by(DeviceRow.role, DeviceRow.device_type)
            ).all()
        )

        devices_by_zone: dict[UUID, list[DeviceRow]] = {
            zone.id: [] for zone in zones
        }

        for device in devices:
            if device.zone_id in devices_by_zone:
                devices_by_zone[device.zone_id].append(device)

        readings_by_device: dict[UUID, ReadingRow] = {}
        device_ids = [device.id for device in devices]

        if device_ids:
            ranked_readings = (
                select(
                    ReadingRow.id.label("reading_id"),
                    func.row_number()
                    .over(
                        partition_by=ReadingRow.device_id,
                        order_by=(
                            ReadingRow.recorded_at.desc(),
                            ReadingRow.id.desc(),
                        ),
                    )
                    .label("row_number"),
                )
                .where(ReadingRow.device_id.in_(device_ids))
                .subquery()
            )

            newest_readings = self._db.scalars(
                select(ReadingRow)
                .join(
                    ranked_readings,
                    ReadingRow.id == ranked_readings.c.reading_id,
                )
                .where(ranked_readings.c.row_number == 1)
            ).all()

            readings_by_device = {
                reading.device_id: reading
                for reading in newest_readings
            }

        zone_dtos = []

        for zone in zones:
            zone_devices = devices_by_zone[zone.id]

            device_dtos = [
                OverviewDeviceDto(
                    id=device.id,
                    device_type=device.device_type,
                    role=device.role,
                    display_name=(
                        device.display_name or device.device_type
                    ),
                )
                for device in zone_devices
            ]

            reading_dtos = [
                OverviewReadingDto(
                    device_id=device.id,
                    value=float(readings_by_device[device.id].value),
                    unit=readings_by_device[device.id].unit,
                    recorded_at=readings_by_device[device.id].recorded_at,
                    tracking_enabled=device.tracking_enabled,
                    sampling_interval_seconds=(
                        device.sampling_interval_seconds
                    ),
                )
                for device in zone_devices
                if device.id in readings_by_device
            ]

            zone_dtos.append(
                OverviewZoneDto(
                    id=zone.id,
                    name=zone.name,
                    moisture_threshold_low=float(
                        zone.moisture_threshold_low
                    ),
                    moisture_threshold_high=float(
                        zone.moisture_threshold_high
                    ),
                    devices=device_dtos,
                    latest_readings=reading_dtos,
                )
            )

        counts = DeviceCountsDto(
            sensor=sum(device.role == "sensor" for device in devices),
            actuator=sum(device.role == "actuator" for device in devices),
        )

        strategy_key = self._automation_repository.get_strategy(
            location_id
        )

        last_recommendation = None

        if strategy_key is not None and zones:
            recommendation = self._automation.evaluate(location_id)

            last_recommendation = OverviewRecommendationDto(
                action=recommendation.action,
                reason=recommendation.reason,
            )

        return LocationOverviewDto(
            location=LocationSummaryDto(
                id=location.id,
                name=location.name,
            ),
            device_counts=counts,
            zones=zone_dtos,
            strategy_key=strategy_key,
            last_recommendation=last_recommendation,
        )
