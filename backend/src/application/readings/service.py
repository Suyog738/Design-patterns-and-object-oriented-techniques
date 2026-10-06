from uuid import UUID

from sqlalchemy.orm import Session

from application.readings.dto import ReadingDto
from domain.devices.entity import Device
from domain.sensors.reading import Reading
from infrastructure.adapters.sensors.mqtt import MqttSensorAdapter
from infrastructure.adapters.sensors.simulation import (
    SimulationSensorAdapter,
)
from infrastructure.adapters.sensors.vendor_stub import (
    VendorStubSensorAdapter,
)
from infrastructure.persistence.models import DeviceRow
from infrastructure.persistence.reading_repository import (
    ReadingRepository,
)


class ReadingIngest:
    def __init__(self, db: Session):
        self._db = db
        self._repository = ReadingRepository(db)

    def take_reading(self, device_id: UUID) -> ReadingDto:
        device = self._db.get(DeviceRow, device_id)

        if device is None:
            raise ValueError("Device not found.")

        if device.role != "sensor":
            raise ValueError("Device is not a sensor.")

        protocol = (device.default_config or {}).get(
            "protocol",
            "simulation",
        )

        domain_device = self._to_domain_device(device)

        if protocol in ("simulation", "sim", "gpio-stub"):
            port = SimulationSensorAdapter()

        elif protocol == "mqtt":
            raise ValueError(
                "MQTT reading requires a translated payload."
            )

        elif protocol == "vendor":
            port = VendorStubSensorAdapter()

        else:
            raise ValueError(
                f"Unsupported sensor protocol: {protocol}"
            )

        reading = port.read(domain_device)

        saved_reading = self._repository.insert(reading)

        return self._to_dto(saved_reading)

    def record(
        self,
        device_id: UUID,
        reading: Reading,
    ) -> ReadingDto:
        if reading.device_id != device_id:
            raise ValueError(
                "Reading device_id does not match "
                "the requested device."
            )

        device = self._db.get(DeviceRow, device_id)

        if device is None:
            raise ValueError("Device not found.")

        saved_reading = self._repository.insert(reading)

        return self._to_dto(saved_reading)

    def list_readings(
        self,
        device_id: UUID,
        limit: int = 20,
    ) -> list[ReadingDto]:
        device = self._db.get(DeviceRow, device_id)

        if device is None:
            raise ValueError("Device not found.")

        if limit < 1:
            raise ValueError("Limit must be at least 1.")

        limit = min(limit, 100)

        readings = self._repository.list_for_device(
            device_id,
            limit,
        )

        return [
            self._to_dto(reading)
            for reading in readings
        ]

    @staticmethod
    def _to_dto(reading: Reading) -> ReadingDto:
        return ReadingDto(
            device_id=reading.device_id,
            value=reading.value,
            unit=reading.unit,
            source=reading.source,
            recorded_at=reading.recorded_at,
        )

    @staticmethod
    def _to_domain_device(
        row: DeviceRow,
    ) -> Device:
        return Device(
            id=row.id,
            device_type=row.device_type,
            role=row.role,
            device_family=row.device_family,
            display_name=row.display_name or "",
            default_config=row.default_config or {},
            zone_id=row.zone_id,
            location_id=row.location_id,
        )