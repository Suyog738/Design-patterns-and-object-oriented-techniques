from datetime import datetime, timezone

from domain.devices.entity import Device
from domain.sensors.reading import Reading


class MqttSensorAdapter:
    def translate(self, device: Device, payload: dict) -> Reading:
        if "value" not in payload:
            raise ValueError("MQTT payload is missing 'value'.")

        if "unit" not in payload:
            raise ValueError("MQTT payload is missing 'unit'.")

        return Reading(
            device_id=device.id,
            value=float(payload["value"]),
            unit=str(payload["unit"]),
            source="mqtt",
            recorded_at=datetime.now(timezone.utc),
        )