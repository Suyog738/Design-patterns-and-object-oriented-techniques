from collections.abc import Callable

from sqlalchemy.orm import Session

from domain.events.bus import EventBus
from domain.events.events import (
    ActuatorStateChanged,
    CommandFailed,
    ReadingCreated,
    ThresholdCrossed,
)
from infrastructure.persistence.alert_repository import AlertRepository
from infrastructure.persistence.models import ZoneRow


SessionFactory = Callable[[], Session]


class MoistureThresholdSubscriber:
    """Turns a low moisture reading into a ThresholdCrossed event."""

    def __init__(self, bus: EventBus, session_factory: SessionFactory) -> None:
        self._bus = bus
        self._session_factory = session_factory

    def on_reading(self, event: ReadingCreated) -> None:
        if event.unit != "vwc" or event.zone_id is None:
            return

        db = self._session_factory()
        try:
            zone = db.get(ZoneRow, event.zone_id)
            if zone is None:
                return
            low = float(zone.moisture_threshold_low)
        finally:
            db.close()

        if event.value < low:  # strictly below
            self._bus.publish(
                ThresholdCrossed(
                    device_id=event.device_id,
                    location_id=event.location_id,
                    zone_id=event.zone_id,
                    value=event.value,
                    threshold=low,
                )
            )


class AlertPersistenceSubscriber:
    """The ONLY place that writes to the alerts table."""

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    def on_threshold(self, event: ThresholdCrossed) -> None:
        self._save(
            location_id=event.location_id,
            zone_id=event.zone_id,
            device_id=event.device_id,
            severity="warning",
            message="Moisture below zone low",
            event_type="threshold.crossed",
        )

    def on_command(self, event: CommandFailed) -> None:
        self._save(
            location_id=event.location_id,
            zone_id=event.zone_id,
            device_id=event.device_id,
            severity="warning",
            message=event.message,
            event_type="command.failed",
        )

    def on_state(self, event: ActuatorStateChanged) -> None:
        if event.state != "error":
            return

        self._save(
            location_id=event.location_id,
            zone_id=event.zone_id,
            device_id=event.device_id,
            severity="critical",
            message="Actuator entered error",
            event_type="state.changed",
        )

    def _save(self, **fields) -> None:
        db = self._session_factory()
        try:
            AlertRepository(db).add(**fields)
        finally:
            db.close()
