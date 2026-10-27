
from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import delete

from application.automation.service import AutomationService
from application.overview.facade import LocationOverviewFacade
from infrastructure.db import get_db
from infrastructure.persistence.models import (
    AutomationRuleRow,
    DeviceRow,
    LocationRow,
    ReadingRow,
    ZoneRow,
)
from main import app


def test_overview_missing_location_returns_404(db):
    app.dependency_overrides[get_db] = lambda: db

    try:
        response = TestClient(app).get(
            f"/api/locations/{uuid4()}/overview"
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 404
    assert response.json()["detail"] == "Location not found."


def test_overview_returns_strategy_and_readings(db):
    location = LocationRow(name=f"Overview Test {uuid4()}")
    db.add(location)
    db.flush()

    location_id = location.id

    try:
        zone_one = ZoneRow(
            location_id=location_id,
            name="Bench 1",
            moisture_threshold_low=0.20,
            moisture_threshold_high=0.45,
            schedule={},
        )
        zone_two = ZoneRow(
            location_id=location_id,
            name="Bench 2",
            moisture_threshold_low=0.30,
            moisture_threshold_high=0.60,
            schedule={},
        )
        db.add_all([zone_one, zone_two])
        db.flush()

        sensor = DeviceRow(
            location_id=location_id,
            zone_id=zone_one.id,
            device_type="moisture_sensor",
            role="sensor",
            device_family="simulation",
            display_name="Bench moisture",
            tracking_enabled=True,
            sampling_interval_seconds=300,
        )

        unassigned_sensor = DeviceRow(
            location_id=location_id,
            zone_id=None,
            device_type="moisture_sensor",
            role="sensor",
            device_family="simulation",
            display_name="Unassigned sensor",
            tracking_enabled=True,
            sampling_interval_seconds=300,
        )

        db.add_all([sensor, unassigned_sensor])
        db.flush()

        db.add(
            ReadingRow(
                device_id=sensor.id,
                value=0.31,
                unit="vwc",
                source="test",
                recorded_at=datetime.now(timezone.utc),
            )
        )
        db.flush()

        facade = LocationOverviewFacade(db)

        overview = facade.get_overview(location_id)

        assert overview.location.id == location_id
        assert overview.strategy_key is None
        assert overview.last_recommendation is None
        assert len(overview.zones) == 2
        assert overview.device_counts.sensor == 1
        assert overview.device_counts.actuator == 0

        all_device_ids = {
            device.id
            for zone in overview.zones
            for device in zone.devices
        }

        assert sensor.id in all_device_ids
        assert unassigned_sensor.id not in all_device_ids

        bench_one = next(
            zone for zone in overview.zones
            if zone.name == "Bench 1"
        )

        assert len(bench_one.latest_readings) == 1

        reading = bench_one.latest_readings[0]

        assert reading.device_id == sensor.id
        assert reading.value == 0.31
        assert reading.unit == "vwc"
        assert reading.tracking_enabled is True
        assert reading.sampling_interval_seconds == 300

        bench_two = next(
            zone for zone in overview.zones
            if zone.name == "Bench 2"
        )

        assert bench_two.devices == []
        assert bench_two.latest_readings == []

        automation = AutomationService(db)
        automation.set_strategy(location_id, "conservative")

        expected = automation.evaluate(location_id)
        updated = facade.get_overview(location_id)

        assert updated.strategy_key == "conservative"
        assert updated.last_recommendation is not None
        assert updated.last_recommendation.action == expected.action
        assert updated.last_recommendation.reason == expected.reason

    finally:
        db.rollback()
        db.execute(
            delete(AutomationRuleRow).where(
                AutomationRuleRow.location_id == location_id
            )
        )
        db.execute(
            delete(DeviceRow).where(
                DeviceRow.location_id == location_id
            )
        )
        db.execute(
            delete(ZoneRow).where(
                ZoneRow.location_id == location_id
            )
        )
        db.execute(
            delete(LocationRow).where(
                LocationRow.id == location_id
            )
        )
        db.commit()
