from application.locations.dto import (
    BuildLocationConfigRequestDto,
    LocationConfigDto,
)
from application.locations.mappers import location_config_to_dto
from domain.locations.config_builder import LocationConfigBuilder
from infrastructure.persistence.location_repository import LocationRepository


class LocationConfigService:
    def __init__(self, repo: LocationRepository):
        self._repo = repo

    def build_and_save(
        self,
        request: BuildLocationConfigRequestDto,
    ) -> LocationConfigDto:
        builder = (
            LocationConfigBuilder()
            .with_location_name(request.location_name)
        )

        for zone in request.zones:
            builder.add_zone(
                name=zone.name,
                moisture_threshold_low=zone.moisture_threshold_low,
                moisture_threshold_high=zone.moisture_threshold_high,
                schedule=zone.schedule,
            )

        # Validation happens here.
        # Invalid configurations never reach the repository.
        config = builder.build()

        location_row, zone_rows = self._repo.save_config(config)

        return location_config_to_dto(
            location_row,
            zone_rows,
        )