from domain.locations.entity import Location, LocationConfig, Zone
from domain.locations.errors import ConfigurationError


class LocationConfigBuilder:
    def __init__(self) -> None:
        self._location_name: str = ""
        self._zones: list[Zone] = []

    def with_location_name(self, name: str) -> "LocationConfigBuilder":
        self._location_name = name.strip()
        return self

    def add_zone(
        self,
        name: str,
        moisture_threshold_low: float,
        moisture_threshold_high: float,
        schedule: dict | None = None,
    ) -> "LocationConfigBuilder":
        zone_name = name.strip()

        self._zones.append(
            Zone(
                id=None,
                name=zone_name,
                moisture_threshold_low=moisture_threshold_low,
                moisture_threshold_high=moisture_threshold_high,
                schedule=schedule.copy() if schedule is not None else {},
            )
        )

        return self

    def build(self) -> LocationConfig:
        # Location name is required.
        if not self._location_name:
            raise ConfigurationError(
                "Location name cannot be empty."
            )

        # At least one zone is required.
        if not self._zones:
            raise ConfigurationError(
                "Location must contain at least one zone."
            )

        # Validate every zone.
        for zone in self._zones:
            if not zone.name:
                raise ConfigurationError(
                    "Zone name cannot be empty."
                )

            if not 0 <= zone.moisture_threshold_low <= 1:
                raise ConfigurationError(
                    f"Invalid low moisture threshold for zone "
                    f"'{zone.name}'. It must be between 0 and 1."
                )

            if not 0 <= zone.moisture_threshold_high <= 1:
                raise ConfigurationError(
                    f"Invalid high moisture threshold for zone "
                    f"'{zone.name}'. It must be between 0 and 1."
                )

            if zone.moisture_threshold_low >= zone.moisture_threshold_high:
                raise ConfigurationError(
                    f"Low moisture threshold must be lower than "
                    f"high threshold for zone '{zone.name}'."
                )

        location = Location(
            id=None,
            name=self._location_name,
        )

        return LocationConfig(
            location=location,
            zones=tuple(self._zones),
        )