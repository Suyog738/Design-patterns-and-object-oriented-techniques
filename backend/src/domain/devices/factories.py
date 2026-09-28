from abc import ABC, abstractmethod

from domain.devices.entity import Device
from domain.sensors.creators import (
    LightSensorCreator,
    MoistureSensorCreator,
)


class DeviceFamilyFactory(ABC):
    @property
    @abstractmethod
    def family_key(self) -> str:
        ...

    @abstractmethod
    def create_device_set(self) -> list[Device]:
        ...


class SimulationDeviceFactory(DeviceFamilyFactory):
    @property
    def family_key(self) -> str:
        return "simulation"

    def create_device_set(self) -> list[Device]:
        moisture_sensor = MoistureSensorCreator().create_sensor(
            "Simulation Moisture Sensor"
        )

        light_sensor = LightSensorCreator().create_sensor(
            "Simulation Light Sensor"
        )

        devices = [
            Device(
                id=None,
                device_type=moisture_sensor.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name=moisture_sensor.display_name
                or "Simulation Moisture Sensor",
                default_config={
                    **moisture_sensor.default_config,
                    "protocol": "sim",
                },
            ),
            Device(
                id=None,
                device_type=light_sensor.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name=light_sensor.display_name
                or "Simulation Light Sensor",
                default_config={
                    **light_sensor.default_config,
                    "protocol": "sim",
                },
            ),
            Device(
                id=None,
                device_type="water_pump",
                role="actuator",
                device_family=self.family_key,
                display_name="Sim irrigation pump",
                default_config={
                    "protocol": "sim",
                },
            ),
            Device(
                id=None,
                device_type="grow_light",
                role="actuator",
                device_family=self.family_key,
                display_name="Sim grow light",
                default_config={
                    "protocol": "sim",
                },
            ),
        ]

        return devices


class EdgeHardwareFactory(DeviceFamilyFactory):
    @property
    def family_key(self) -> str:
        return "edge"

    def create_device_set(self) -> list[Device]:
        moisture_sensor = MoistureSensorCreator().create_sensor(
            "Edge Moisture Sensor"
        )

        light_sensor = LightSensorCreator().create_sensor(
            "Edge Light Sensor"
        )

        devices = [
            Device(
                id=None,
                device_type=moisture_sensor.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name=moisture_sensor.display_name
                or "Edge Moisture Sensor",
                default_config={
                    **moisture_sensor.default_config,
                    "protocol": "gpio-stub",
                },
            ),
            Device(
                id=None,
                device_type=light_sensor.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name=light_sensor.display_name
                or "Edge Light Sensor",
                default_config={
                    **light_sensor.default_config,
                    "protocol": "gpio-stub",
                },
            ),
            Device(
                id=None,
                device_type="water_pump",
                role="actuator",
                device_family=self.family_key,
                display_name="Edge irrigation pump",
                default_config={
                    "protocol": "gpio-stub",
                },
            ),
            Device(
                id=None,
                device_type="grow_light",
                role="actuator",
                device_family=self.family_key,
                display_name="Edge grow light",
                default_config={
                    "protocol": "gpio-stub",
                },
            ),
        ]

        return devices


def get_family_factory(family: str) -> DeviceFamilyFactory:
    factories: dict[str, DeviceFamilyFactory] = {
        "simulation": SimulationDeviceFactory(),
        "edge": EdgeHardwareFactory(),
    }

    try:
        return factories[family]
    except KeyError:
        raise ValueError(f"Unknown device family: {family}")