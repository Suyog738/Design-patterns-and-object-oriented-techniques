from domain.sensors.creators import get_creator
from domain.sensors.entity import Sensor
from infrastructure.persistence.device_repository import DeviceRepository


class SensorService:
    def __init__(self, repo: DeviceRepository):
        self._repo = repo

    def create_sensor(
        self,
        sensor_type: str,
        display_name: str | None = None,
    ) -> Sensor:
        creator = get_creator(sensor_type)

        sensor = creator.create_sensor(
            display_name=display_name,
        )

        return self._repo.save_sensor(sensor)

    def list_sensors(self) -> list[Sensor]:
        return self._repo.list_sensors()