from abc import ABC, abstractmethod

from .entity import Sensor


class SensorCreator(ABC):
    @abstractmethod
    def create_sensor(
        self,
        display_name: str | None = None,
    ) -> Sensor:
        """Create and return a sensor with its default configuration."""
        ...


class MoistureSensorCreator(SensorCreator):
    def create_sensor(
        self,
        display_name: str | None = None,
    ) -> Sensor:
        return Sensor(
            id=None,
            device_type="moisture_sensor",
            display_name=display_name,
            default_config={
                "sampling_interval_seconds": 300,
                "unit": "vwc",
                "threshold": 30,
            },
        )


class LightSensorCreator(SensorCreator):
    def create_sensor(
        self,
        display_name: str | None = None,
    ) -> Sensor:
        return Sensor(
            id=None,
            device_type="light_sensor",
            display_name=display_name,
            default_config={
                "sampling_interval_seconds": 60,
                "unit": "lux",
            },
        )


def get_creator(sensor_type: str) -> SensorCreator:
    creators: dict[str, SensorCreator] = {
        "moisture": MoistureSensorCreator(),
        "light": LightSensorCreator(),
    }

    try:
        return creators[sensor_type]
    except KeyError:
        raise ValueError(f"Unknown sensor type: {sensor_type}")