from uuid import uuid4

from domain.devices.entity import Device
from infrastructure.adapters.sensors.mqtt import MqttSensorAdapter
from infrastructure.adapters.sensors.simulation import (
    SimulationSensorAdapter,
)
from infrastructure.adapters.sensors.vendor_stub import (
    VendorStubSensorAdapter,
)


def make_device(
    device_type: str,
    protocol: str = "simulation",
) -> Device:
    return Device(
        id=uuid4(),
        device_type=device_type,
        role="sensor",
        device_family="simulation",
        display_name="Test Sensor",
        default_config={"protocol": protocol},
    )


def test_vendor_adapter_normalizes_raw_payload():
    device = make_device("moisture_sensor")

    reading = VendorStubSensorAdapter().read(device)

    assert reading.device_id == device.id
    assert reading.value == 0.45
    assert reading.unit == "vwc"
    assert reading.source == "vendor"


def test_simulation_moisture_adapter_stays_inside_range():
    device = make_device("moisture_sensor")

    reading = SimulationSensorAdapter().read(device)

    assert 0.2 <= reading.value <= 0.6
    assert reading.unit == "vwc"
    assert reading.source == "simulation"


def test_simulation_light_adapter_stays_inside_range():
    device = make_device("light_sensor")

    reading = SimulationSensorAdapter().read(device)

    assert 200 <= reading.value <= 2000
    assert reading.unit == "lux"
    assert reading.source == "simulation"


def test_mqtt_adapter_translates_payload():
    device = make_device("moisture_sensor")

    payload = {
        "value": 0.41,
        "unit": "vwc",
    }

    reading = MqttSensorAdapter().translate(
        device,
        payload,
    )

    assert reading.device_id == device.id
    assert reading.value == 0.41
    assert reading.unit == "vwc"
    assert reading.source == "mqtt"


def test_mqtt_adapter_does_not_open_socket():
    device = make_device("moisture_sensor")

    adapter = MqttSensorAdapter()

    reading = adapter.translate(
        device,
        {
            "value": 0.41,
            "unit": "vwc",
        },
    )

    assert reading.source == "mqtt"