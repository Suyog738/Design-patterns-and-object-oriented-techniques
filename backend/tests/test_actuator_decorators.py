from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from domain.actuators.ports import ActuatorPolicyError, ActuatorPort
from infrastructure.adapters.actuators.logging_decorator import (
    LoggingActuatorDecorator,
)
from infrastructure.adapters.actuators.max_runtime_decorator import (
    MaxRunTimeActuatorDecorator,
)


NOW = datetime(2026, 11, 4, 12, 0, tzinfo=timezone.utc)


class SpyActuator(ActuatorPort):
    def __init__(self):
        self.calls = []

    def apply(self, device_id, command, payload):
        self.calls.append((device_id, command, payload))


class FakeStateRepo:
    def __init__(self, state, updated_at):
        self._snapshot = (state, updated_at)

    def get_snapshot(self, device_id):
        return self._snapshot


class FakeLogRepo:
    def __init__(self):
        self.rows = []

    def add(self, device_id, success, policy_applied, message):
        self.rows.append(
            {
                "device_id": device_id,
                "success": success,
                "policy_applied": policy_applied,
                "message": message,
            }
        )


def make_stack(state, minutes_ago):
    spy = SpyActuator()
    log_repo = FakeLogRepo()
    port = LoggingActuatorDecorator(
        MaxRunTimeActuatorDecorator(
            spy,
            FakeStateRepo(state, NOW - timedelta(minutes=minutes_ago)),
            clock=lambda: NOW,
        ),
        log_repo,
    )
    return port, spy, log_repo


def test_max_runtime_does_not_call_inner():
    spy = SpyActuator()
    decorator = MaxRunTimeActuatorDecorator(
        spy,
        FakeStateRepo("running", NOW - timedelta(minutes=30)),
        clock=lambda: NOW,
    )

    with pytest.raises(ActuatorPolicyError) as exc_info:
        decorator.apply(uuid4(), "start_pump", {})

    assert exc_info.value.policy == "maxRunTime"
    assert spy.calls == []


def test_failed_policy_writes_execution_row():
    port, spy, log_repo = make_stack("running", minutes_ago=45)
    device_id = uuid4()

    with pytest.raises(ActuatorPolicyError):
        port.apply(device_id, "stop_pump", {})

    assert spy.calls == []
    assert log_repo.rows == [
        {
            "device_id": device_id,
            "success": False,
            "policy_applied": ["maxRunTime", "logging"],
            "message": "Max run time exceeded",
        }
    ]


def test_success_writes_logging_row_and_calls_inner():
    port, spy, log_repo = make_stack("idle", minutes_ago=120)
    device_id = uuid4()

    port.apply(device_id, "unknown_command", {})

    assert len(spy.calls) == 1
    assert log_repo.rows[0]["success"] is True
    assert log_repo.rows[0]["policy_applied"] == ["logging"]
    assert log_repo.rows[0]["message"] is None


def test_running_under_limit_is_allowed():
    port, spy, log_repo = make_stack("running", minutes_ago=29)

    port.apply(uuid4(), "stop_pump", {})

    assert len(spy.calls) == 1
    assert log_repo.rows[0]["success"] is True
