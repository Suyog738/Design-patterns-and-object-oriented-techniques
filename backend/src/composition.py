from collections.abc import Callable

from sqlalchemy.orm import Session

from application.alerts.subscribers import (
    AlertPersistenceSubscriber,
    MoistureThresholdSubscriber,
)
from domain.events.bus import EventBus
from domain.events.events import (
    ActuatorStateChanged,
    CommandFailed,
    ReadingCreated,
    ThresholdCrossed,
)
from infrastructure.db import SessionLocal


def build_event_bus(
    session_factory: Callable[[], Session] = SessionLocal,
) -> EventBus:
    bus = EventBus()

    moisture = MoistureThresholdSubscriber(bus, session_factory)
    alerts = AlertPersistenceSubscriber(session_factory)

    bus.subscribe(ReadingCreated, moisture.on_reading)
    bus.subscribe(ThresholdCrossed, alerts.on_threshold)
    bus.subscribe(CommandFailed, alerts.on_command)
    bus.subscribe(ActuatorStateChanged, alerts.on_state)

    return bus


# One bus for the whole app.
event_bus = build_event_bus()


def get_event_bus() -> EventBus:
    """FastAPI dependency: inject the shared bus into services."""
    return event_bus
