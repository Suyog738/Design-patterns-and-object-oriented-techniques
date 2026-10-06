from datetime import datetime, timezone

from domain.devices.entity import Device
from domain.sensors.ports import SensorPort
from domain.sensors.reading import Reading


class VendorStubSensorAdapter(SensorPort):
    def read(self, device: Device) -> Reading:
        raw_payload = {
            "reading": 0.45,
            "measurement": "vwc",
        }

        return Reading(
            device_id=device.id,
            value=float(raw_payload["reading"]),
            unit=raw_payload["measurement"],
            source="vendor",
            recorded_at=datetime.now(timezone.utc),
        )