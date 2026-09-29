from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.locations.config_service import LocationConfigService
from application.locations.dto import (
    BuildLocationConfigRequestDto,
    LocationConfigDto,
    ZoneConfigRequestDto,
)
from application.locations.mappers import location_config_to_dto
from application.locations.zone_assignment_service import (
    ZoneAssignmentService,
)
from domain.locations.config_builder import LocationConfigBuilder
from domain.locations.errors import ConfigurationError
from infrastructure.db import get_db
from infrastructure.persistence.location_repository import LocationRepository
from infrastructure.persistence.models import LocationRow

router = APIRouter(
    prefix="/api/locations",
    tags=["locations"],
)


def get_location_service(
    db: Session = Depends(get_db),
) -> LocationConfigService:
    return LocationConfigService(LocationRepository(db))


@router.post(
    "/config",
    response_model=LocationConfigDto,
    status_code=status.HTTP_201_CREATED,
)
def create_location_config(
    request: BuildLocationConfigRequestDto,
    service: LocationConfigService = Depends(get_location_service),
):
    try:
        return service.build_and_save(request)
    except ConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("")
def list_locations(
    db: Session = Depends(get_db),
):
    locations = (
        db.query(LocationRow)
        .order_by(LocationRow.created_at)
        .all()
    )

    return [
        {
            "id": location.id,
            "name": location.name,
        }
        for location in locations
    ]


@router.get(
    "/{location_id}/config",
    response_model=LocationConfigDto,
)
def get_location_config(
    location_id: UUID,
    db: Session = Depends(get_db),
):
    repository = LocationRepository(db)

    result = repository.get_config(location_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found.",
        )

    location_row, zone_rows = result

    return location_config_to_dto(
        location_row,
        zone_rows,
    )


@router.delete(
    "/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_location(
    location_id: UUID,
    db: Session = Depends(get_db),
):
    repository = LocationRepository(db)

    location = repository.get_location(location_id)

    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found.",
        )

    repository.delete_location(location)


@router.post(
    "/{location_id}/zones",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
)
def add_zone(
    location_id: UUID,
    request: ZoneConfigRequestDto,
    db: Session = Depends(get_db),
):
    repository = LocationRepository(db)

    location = repository.get_location(location_id)

    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found.",
        )

    try:
        builder = (
            LocationConfigBuilder()
            .with_location_name(location.name)
            .add_zone(
                name=request.name,
                moisture_threshold_low=request.moisture_threshold_low,
                moisture_threshold_high=request.moisture_threshold_high,
                schedule=request.schedule,
            )
        )

        builder.build()

    except ConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    zone = repository.add_zone(
        location_id=location_id,
        name=request.name.strip(),
        moisture_threshold_low=request.moisture_threshold_low,
        moisture_threshold_high=request.moisture_threshold_high,
        schedule=request.schedule,
    )

    return {
        "id": zone.id,
        "location_id": zone.location_id,
        "name": zone.name,
        "moisture_threshold_low": float(
            zone.moisture_threshold_low
        ),
        "moisture_threshold_high": float(
            zone.moisture_threshold_high
        ),
        "schedule": zone.schedule or {},
    }


@router.patch(
    "/{location_id}/zones/{zone_id}",
    response_model=dict,
)
def update_zone(
    location_id: UUID,
    zone_id: UUID,
    request: ZoneConfigRequestDto,
    db: Session = Depends(get_db),
):
    repository = LocationRepository(db)

    location = repository.get_location(location_id)

    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found.",
        )

    zone = repository.get_zone(zone_id)

    if zone is None or zone.location_id != location_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found.",
        )

    try:
        builder = (
            LocationConfigBuilder()
            .with_location_name(location.name)
            .add_zone(
                name=request.name,
                moisture_threshold_low=request.moisture_threshold_low,
                moisture_threshold_high=request.moisture_threshold_high,
                schedule=request.schedule,
            )
        )

        builder.build()

    except ConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    zone = repository.update_zone(
        zone_row=zone,
        name=request.name.strip(),
        moisture_threshold_low=request.moisture_threshold_low,
        moisture_threshold_high=request.moisture_threshold_high,
        schedule=request.schedule,
    )

    return {
        "id": zone.id,
        "location_id": zone.location_id,
        "name": zone.name,
        "moisture_threshold_low": float(
            zone.moisture_threshold_low
        ),
        "moisture_threshold_high": float(
            zone.moisture_threshold_high
        ),
        "schedule": zone.schedule or {},
    }


@router.delete(
    "/{location_id}/zones/{zone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_zone(
    location_id: UUID,
    zone_id: UUID,
    db: Session = Depends(get_db),
):
    repository = LocationRepository(db)

    location = repository.get_location(location_id)

    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found.",
        )

    zone = repository.get_zone(zone_id)

    if zone is None or zone.location_id != location_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found.",
        )

    if repository.count_zones(location_id) <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A location must contain at least one zone.",
        )

    repository.delete_zone(zone)


@router.get(
    "/{location_id}/zones/{zone_id}/devices",
)
def list_zone_devices(
    location_id: UUID,
    zone_id: UUID,
    db: Session = Depends(get_db),
):
    service = ZoneAssignmentService(db)

    try:
        devices = service.list_devices(
            location_id=location_id,
            zone_id=zone_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return [
        {
            "id": device.id,
            "device_type": device.device_type,
            "role": device.role,
            "device_family": device.device_family,
            "display_name": device.display_name,
            "default_config": device.default_config,
        }
        for device in devices
    ]