import pytest

from domain.locations.config_builder import LocationConfigBuilder
from domain.locations.errors import ConfigurationError


def test_build_success():
    config = (
        LocationConfigBuilder()
        .with_location_name("Main Greenhouse")
        .add_zone(
            name="Tomatoes",
            moisture_threshold_low=0.30,
            moisture_threshold_high=0.70,
            schedule={"monday": ["08:00"]},
        )
        .build()
    )

    assert config.location.name == "Main Greenhouse"
    assert len(config.zones) == 1
    assert config.zones[0].name == "Tomatoes"
    assert config.zones[0].moisture_threshold_low == 0.30
    assert config.zones[0].moisture_threshold_high == 0.70
    assert config.zones[0].schedule == {
        "monday": ["08:00"]
    }


def test_build_requires_name():
    builder = (
        LocationConfigBuilder()
        .add_zone(
            name="Tomatoes",
            moisture_threshold_low=0.30,
            moisture_threshold_high=0.70,
        )
    )

    with pytest.raises(
        ConfigurationError,
        match="Location name cannot be empty",
    ):
        builder.build()


def test_build_requires_zones():
    builder = (
        LocationConfigBuilder()
        .with_location_name("Main Greenhouse")
    )

    with pytest.raises(
        ConfigurationError,
        match="Location must contain at least one zone",
    ):
        builder.build()


def test_build_rejects_invalid_thresholds():
    # Low threshold cannot be negative.
    with pytest.raises(ConfigurationError):
        (
            LocationConfigBuilder()
            .with_location_name("Main Greenhouse")
            .add_zone(
                name="Tomatoes",
                moisture_threshold_low=-0.10,
                moisture_threshold_high=0.70,
            )
            .build()
        )

    # High threshold cannot be greater than 1.
    with pytest.raises(ConfigurationError):
        (
            LocationConfigBuilder()
            .with_location_name("Main Greenhouse")
            .add_zone(
                name="Tomatoes",
                moisture_threshold_low=0.30,
                moisture_threshold_high=1.20,
            )
            .build()
        )

    # Low threshold must be lower than high threshold.
    with pytest.raises(ConfigurationError):
        (
            LocationConfigBuilder()
            .with_location_name("Main Greenhouse")
            .add_zone(
                name="Tomatoes",
                moisture_threshold_low=0.80,
                moisture_threshold_high=0.50,
            )
            .build()
        )