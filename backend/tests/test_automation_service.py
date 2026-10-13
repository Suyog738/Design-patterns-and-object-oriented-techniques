from uuid import uuid4

from application.automation.service import AutomationService
from infrastructure.persistence.models import (
    DeviceRow,
    LocationRow,
    ReadingRow,
    ZoneRow,
)


def create_location(db):
    location = LocationRow(
        id=uuid4(),
        name="Test Location",
    )

    db.add(location)
    db.flush()

    zone = ZoneRow(
        id=uuid4(),
        location_id=location.id,
        name="Test Zone",
        moisture_threshold_low=0.25,
        moisture_threshold_high=0.45,
        schedule={},
    )

    db.add(zone)
    db.commit()
    db.refresh(location)
    db.refresh(zone)

    return location, zone


def create_moisture_sensor(
    db,
    location_id,
    zone_id,
):
    device = DeviceRow(
        id=uuid4(),
        device_type="moisture_sensor",
        role="sensor",
        device_family="simulation",
        display_name="Test Moisture Sensor",
        default_config={"protocol": "simulation"},
        location_id=location_id,
        zone_id=zone_id,
    )

    db.add(device)
    db.commit()
    db.refresh(device)

    return device


def add_reading(
    db,
    device_id,
    value,
):
    reading = ReadingRow(
        id=uuid4(),
        device_id=device_id,
        value=value,
        unit="vwc",
        source="simulation",
    )

    db.add(reading)
    db.commit()
    db.refresh(reading)

    return reading


def test_set_strategy_and_evaluate(db):
    location, zone = create_location(db)

    device = create_moisture_sensor(
        db,
        location.id,
        zone.id,
    )

    add_reading(
        db,
        device.id,
        0.40,
    )

    service = AutomationService(db)

    service.set_strategy(
        location.id,
        "conservative",
    )

    result = service.evaluate(location.id)

    assert result.location_id == location.id
    assert result.strategy_key == "conservative"
    assert result.action == "wait"


def test_aggressive_strategy_changes_recommendation(db):
    location, zone = create_location(db)

    device = create_moisture_sensor(
        db,
        location.id,
        zone.id,
    )

    add_reading(
        db,
        device.id,
        0.40,
    )

    service = AutomationService(db)

    service.set_strategy(
        location.id,
        "conservative",
    )

    conservative = service.evaluate(location.id)

    service.set_strategy(
        location.id,
        "aggressive",
    )

    aggressive = service.evaluate(location.id)

    assert conservative.action == "wait"
    assert aggressive.action == "irrigate"
    assert conservative.action != aggressive.action


def test_missing_location_raises_error(db):
    service = AutomationService(db)

    try:
        service.evaluate(uuid4())
        assert False
    except ValueError as error:
        assert str(error) == "Location not found."