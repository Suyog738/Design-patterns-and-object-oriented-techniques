import importlib
import inspect
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from application.commands.service import CommandService
from application.readings.service import ReadingIngest
from composition import build_event_bus
from domain.events.bus import EventBus
from domain.events.events import ReadingCreated
from domain.sensors.reading import Reading
from infrastructure.db import SessionLocal, get_db
from infrastructure.persistence.alert_repository import AlertRepository
from infrastructure.persistence.models import (
    ActuatorStateRow,
    AlertRow,
    DeviceRow,
    LocationRow,
    ZoneRow,
)
from infrastructure.persistence.reading_repository import ReadingRepository
from main import app


# ---------- helpers ----------

def make_bench(db):
    location = LocationRow(name=f"Alerts Test {uuid4()}")
    db.add(location)
    db.flush()

    zone = ZoneRow(
        location_id=location.id,
        name="Bench 1",
        moisture_threshold_low=0.20,
        moisture_threshold_high=0.45,
        schedule={},
    )
    db.add(zone)
    db.commit()
    return location.id, zone.id


def make_sensor(db, *, tracking=True, location_id=None, zone_id=None):
    device = DeviceRow(
        device_type="moisture_sensor",
        role="sensor",
        device_family="simulation",
        display_name="Alerts test sensor",
        default_config={"protocol": "sim"},
        tracking_enabled=tracking,
        location_id=location_id,
        zone_id=zone_id,
    )
    db.add(device)
    db.commit()
    return device.id


def make_pump(db, *, state="idle", minutes_in_state=0):
    device = DeviceRow(
        device_type="water_pump",
        role="actuator",
        device_family="simulation",
        display_name="Alerts test pump",
        default_config={},
    )
    db.add(device)
    db.flush()

    db.add(
        ActuatorStateRow(
            device_id=device.id,
            state=state,
            updated_at=datetime.now(timezone.utc)
            - timedelta(minutes=minutes_in_state),
        )
    )
    db.commit()
    return device.id


def cleanup(db, device_ids, location_id=None):
    db.rollback()
    # alerts use SET NULL, so delete them explicitly first.
    db.execute(delete(AlertRow).where(AlertRow.device_id.in_(device_ids)))
    db.execute(delete(DeviceRow).where(DeviceRow.id.in_(device_ids)))
    if location_id is not None:
        db.execute(delete(LocationRow).where(LocationRow.id == location_id))
    db.commit()


def alerts_for(db, device_id):
    db.expire_all()
    return [
        row
        for row in AlertRepository(db).list_alerts(status="all", limit=200)
        if row.device_id == device_id
    ]


# ---------- tests ----------

def test_tracking_on_publishes_reading_created(db):
    device_id = make_sensor(db, tracking=True)
    bus = EventBus()
    received = []
    bus.subscribe(ReadingCreated, received.append)

    try:
        ReadingIngest(db, bus).take_reading(device_id)

        assert len(received) == 1
        assert received[0].device_id == device_id
    finally:
        cleanup(db, [device_id])


def test_tracking_off_stores_reading_but_does_not_publish(db):
    device_id = make_sensor(db, tracking=False)
    bus = EventBus()
    received = []
    bus.subscribe(ReadingCreated, received.append)

    try:
        ReadingIngest(db, bus).take_reading(device_id)

        assert received == []
        assert len(ReadingRepository(db).list_for_device(device_id)) == 1
    finally:
        cleanup(db, [device_id])


def test_low_moisture_inserts_threshold_alert_for_zone(db):
    location_id, zone_id = make_bench(db)
    device_id = make_sensor(db, location_id=location_id, zone_id=zone_id)
    bus = build_event_bus(SessionLocal)

    try:
        ReadingIngest(db, bus).record(
            device_id,
            Reading(
                device_id=device_id,
                value=0.10,
                unit="vwc",
                source="mqtt",
                recorded_at=datetime.now(timezone.utc),
            ),
        )

        db.expire_all()
        rows = AlertRepository(db).list_alerts(zone_id=zone_id)

        assert len(rows) == 1
        assert rows[0].event_type == "threshold.crossed"
        assert rows[0].severity == "warning"
        assert rows[0].message == "Moisture below zone low"
        assert rows[0].zone_id == zone_id
        assert rows[0].location_id == location_id
    finally:
        cleanup(db, [device_id], location_id)


def test_failed_stop_pump_inserts_command_failed_alert(db):
    # Unassigned pump running for 45 min -> max run time blocks stop_pump.
    device_id = make_pump(db, state="running", minutes_in_state=45)
    bus = build_event_bus(SessionLocal)

    try:
        log = CommandService(db, bus=bus).submit("stop_pump", device_id, {})
        assert log.status == "failed"

        rows = alerts_for(db, device_id)
        assert len(rows) == 1
        assert rows[0].event_type == "command.failed"
        assert rows[0].message == "Max run time exceeded"
        assert rows[0].location_id is None
        assert rows[0].zone_id is None
    finally:
        cleanup(db, [device_id])


def test_transition_to_error_inserts_critical_alert(db):
    device_id = make_pump(db, state="idle")
    app.dependency_overrides[get_db] = lambda: db

    try:
        response = TestClient(app).post(
            f"/api/devices/{device_id}/transition",
            json={"target": "error"},
        )
        assert response.status_code == 200

        rows = alerts_for(db, device_id)
        assert len(rows) == 1
        assert rows[0].event_type == "state.changed"
        assert rows[0].severity == "critical"
        assert rows[0].message == "Actuator entered error"
    finally:
        app.dependency_overrides.pop(get_db, None)
        cleanup(db, [device_id])


def test_alerts_status_must_be_valid(db):
    app.dependency_overrides[get_db] = lambda: db
    try:
        response = TestClient(app).get("/api/alerts?status=banana")
        assert response.status_code == 400
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.mark.parametrize(
    "module_name",
    [
        "application.readings.service",
        "application.commands.service",
        "application.actuators.transition_service",
    ],
)
def test_publishers_do_not_import_alert_repository(module_name):
    source = inspect.getsource(importlib.import_module(module_name))

    assert "AlertRepository" not in source
    assert "AlertRow" not in source
