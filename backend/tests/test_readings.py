from datetime import datetime, timedelta, timezone
from uuid import uuid4

from domain.devices.entity import Device
from infrastructure.persistence.models import DeviceRow
from infrastructure.persistence.reading_repository import ReadingRepository


def create_sensor(
    db,
    *,
    protocol: str = "simulation",
    tracking_enabled: bool = True,
    sampling_interval_seconds: int = 30,
):
    device = DeviceRow(
        id=uuid4(),
        device_type="moisture_sensor",
        role="sensor",
        device_family="simulation",
        display_name="Test Sensor",
        default_config={"protocol": protocol},
        tracking_enabled=tracking_enabled,
        sampling_interval_seconds=sampling_interval_seconds,
    )

    db.add(device)
    db.commit()
    db.refresh(device)

    return device


def test_read_inserts_sensor_reading(db):
    from application.readings.service import ReadingIngest

    device = create_sensor(db)

    service = ReadingIngest(db)

    result = service.take_reading(device.id)

    assert result.device_id == device.id
    assert result.source == "simulation"

    repository = ReadingRepository(db)
    readings = repository.list_for_device(device.id, limit=10)

    assert len(readings) == 1
    assert readings[0].device_id == device.id
    assert readings[0].source == "simulation"


def test_sampler_inserts_when_interval_has_elapsed(db):
    from application.readings.sampler import SimulationSampler

    device = create_sensor(
        db,
        sampling_interval_seconds=30,
    )

    sampler = SimulationSampler(db)

    now = datetime.now(timezone.utc)

    sampler.run_once(now)

    repository = ReadingRepository(db)

    readings = repository.list_for_device(
        device.id,
        limit=10,
    )

    assert len(readings) == 1


def test_sampler_skips_second_call_inside_interval(db):
    from application.readings.sampler import SimulationSampler

    device = create_sensor(
        db,
        sampling_interval_seconds=30,
    )

    sampler = SimulationSampler(db)

    now = datetime.now(timezone.utc)

    sampler.run_once(now)
    sampler.run_once(now + timedelta(seconds=10))

    repository = ReadingRepository(db)

    readings = repository.list_for_device(
        device.id,
        limit=10,
    )

    assert len(readings) == 1


def test_sampler_inserts_after_interval_has_elapsed(db):
    from application.readings.sampler import SimulationSampler

    device = create_sensor(
        db,
        sampling_interval_seconds=30,
    )

    sampler = SimulationSampler(db)

    now = datetime.now(timezone.utc)

    sampler.run_once(now)
    sampler.run_once(now + timedelta(seconds=31))

    repository = ReadingRepository(db)

    readings = repository.list_for_device(
        device.id,
        limit=10,
    )

    assert len(readings) == 2


def test_sampler_skips_disabled_device(db):
    from application.readings.sampler import SimulationSampler

    device = create_sensor(
        db,
        tracking_enabled=False,
    )

    sampler = SimulationSampler(db)

    sampler.run_once(datetime.now(timezone.utc))

    repository = ReadingRepository(db)

    readings = repository.list_for_device(
        device.id,
        limit=10,
    )

    assert len(readings) == 0


def test_sampler_skips_mqtt_device(db):
    from application.readings.sampler import SimulationSampler

    device = create_sensor(
        db,
        protocol="mqtt",
    )

    sampler = SimulationSampler(db)

    sampler.run_once(datetime.now(timezone.utc))

    repository = ReadingRepository(db)

    readings = repository.list_for_device(
        device.id,
        limit=10,
    )

    assert len(readings) == 0