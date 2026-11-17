from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from application.commands.service import CommandService
from infrastructure.db import get_db
from infrastructure.persistence.models import (
    ActuatorExecutionLogRow,
    ActuatorStateRow,
    CommandLogRow,
    DeviceRow,
)
from main import app


def make_actuator(db, state: str | None = None):
    device = DeviceRow(
        device_type="water_pump",
        role="actuator",
        device_family="simulation",
        display_name=f"Test pump {uuid4()}",
        default_config={},
    )
    db.add(device)
    db.flush()

    if state is not None:
        db.add(ActuatorStateRow(device_id=device.id, state=state))

    db.commit()
    return device.id


def cleanup(db, device_id):
    db.rollback()
    # FK ondelete=CASCADE removes command_log, actuator_states, execution log.
    db.execute(delete(DeviceRow).where(DeviceRow.id == device_id))
    db.commit()


def command_rows(db, device_id):
    return db.scalars(
        select(CommandLogRow).where(CommandLogRow.device_id == device_id)
    ).all()


def test_illegal_command_rejected_logged(db):
    device_id = make_actuator(db, state="running")
    app.dependency_overrides[get_db] = lambda: db

    try:
        response = TestClient(app).post(
            "/api/commands",
            json={
                "command_type": "start_pump",
                "device_id": str(device_id),
                "payload": {},
            },
        )

        assert response.status_code == 409
        assert response.json()["status"] == "rejected"

        db.expire_all()
        assert db.get(ActuatorStateRow, device_id).state == "running"
        assert [row.status for row in command_rows(db, device_id)] == ["rejected"]

        # Guard stopped it before the port: no execution-log row.
        executions = db.scalars(
            select(ActuatorExecutionLogRow).where(
                ActuatorExecutionLogRow.device_id == device_id
            )
        ).all()
        assert executions == []

        history = TestClient(app).get("/api/commands?limit=200").json()
        assert any(row["device_id"] == str(device_id) for row in history)
    finally:
        app.dependency_overrides.pop(get_db, None)
        cleanup(db, device_id)


def test_start_pump_transitions_to_running(db):
    device_id = make_actuator(db, state="idle")

    try:
        log = CommandService(db).submit("start_pump", device_id, {})

        assert log.status == "success"
        assert log.error_message is None

        db.expire_all()
        assert db.get(ActuatorStateRow, device_id).state == "running"
    finally:
        cleanup(db, device_id)


def test_unknown_command_returns_400_without_row(db):
    device_id = make_actuator(db, state="idle")
    app.dependency_overrides[get_db] = lambda: db

    try:
        response = TestClient(app).post(
            "/api/commands",
            json={
                "command_type": "launch_rocket",
                "device_id": str(device_id),
                "payload": {},
            },
        )

        assert response.status_code == 400
        assert command_rows(db, device_id) == []
    finally:
        app.dependency_overrides.pop(get_db, None)
        cleanup(db, device_id)
