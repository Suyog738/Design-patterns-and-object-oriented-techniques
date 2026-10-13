from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from application.automation.dto import RecommendationDto
from domain.automation.context import LocationAutomationContext
from domain.automation.strategy import get_strategy
from infrastructure.persistence.models import (
    DeviceRow,
    LocationRow,
    ReadingRow,
    ZoneRow,
)
from infrastructure.persistence.automation_repository import (
    AutomationRepository,
)


class AutomationService:
    def __init__(self, db: Session):
        self._db = db
        self._repository = AutomationRepository(db)

    def set_strategy(
        self,
        location_id: UUID,
        strategy_key: str,
    ) -> None:
        location = self._db.get(LocationRow, location_id)

        if location is None:
            raise ValueError("Location not found.")

        get_strategy(strategy_key)

        self._repository.set_strategy(
            location_id,
            strategy_key,
        )

    def evaluate(
        self,
        location_id: UUID,
    ) -> RecommendationDto:
        location = self._db.get(LocationRow, location_id)

        if location is None:
            raise ValueError("Location not found.")

        strategy_key = self._repository.get_strategy(
            location_id
        )

        if strategy_key is None:
            raise ValueError(
                "No automation strategy configured."
            )

        strategy = get_strategy(strategy_key)

        zone_statement = (
            select(ZoneRow)
            .where(
                ZoneRow.location_id == location_id
            )
            .order_by(ZoneRow.name)
        )

        zone = self._db.scalars(zone_statement).first()

        if zone is None:
            raise ValueError("No zone found for location.")

        moisture_statement = (
            select(ReadingRow)
            .join(
                DeviceRow,
                DeviceRow.id == ReadingRow.device_id,
            )
            .where(
                DeviceRow.role == "sensor",
                DeviceRow.device_type == "moisture_sensor",
                DeviceRow.zone_id == zone.id,
                ReadingRow.unit == "vwc",
            )
            .order_by(
                ReadingRow.recorded_at.desc()
            )
            .limit(1)
        )

        moisture_reading = self._db.scalars(
            moisture_statement
        ).first()

        light_statement = (
            select(ReadingRow)
            .join(
                DeviceRow,
                DeviceRow.id == ReadingRow.device_id,
            )
            .where(
                DeviceRow.role == "sensor",
                DeviceRow.device_type == "light_sensor",
                DeviceRow.zone_id == zone.id,
                ReadingRow.unit == "lux",
            )
            .order_by(
                ReadingRow.recorded_at.desc()
            )
            .limit(1)
        )

        light_reading = self._db.scalars(
            light_statement
        ).first()

        context = LocationAutomationContext(
            location_id=location.id,
            zone_id=zone.id,
            moisture=(
                float(moisture_reading.value)
                if moisture_reading is not None
                else None
            ),
            light=(
                float(light_reading.value)
                if light_reading is not None
                else None
            ),
            moisture_low=float(
                zone.moisture_threshold_low
            ),
            moisture_high=float(
                zone.moisture_threshold_high
            ),
        )

        recommendation = strategy.decide(context)

        return RecommendationDto(
            location_id=location.id,
            strategy_key=strategy_key,
            action=recommendation.action,
            reason=recommendation.reason,
            score=recommendation.score,
        )