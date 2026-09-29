from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from application.devices.service import DeviceFamilyService
from application.locations.dto import ZoneAssignmentRequestDto
from application.locations.zone_assignment_service import (
    ZoneAssignmentService,
)
from domain.devices.entity import Device
from domain.devices.factories import get_family_factory
from infrastructure.db import get_db
from infrastructure.persistence.device_repository import DeviceRepository

router = APIRouter(
    prefix="/api/devices",
    tags=["devices"],
)


class DeviceDto(BaseModel):
    id: UUID
    device_type: str
    role: str
    device_family: str
    display_name: str
    default_config: dict
    zone_id: UUID | None = None
    location_id: UUID | None = None


def device_to_dto(device: Device) -> DeviceDto:
    if device.id is None:
        raise ValueError(
            "Device must be saved before converting to DTO"
        )

    return DeviceDto(
        id=device.id,
        device_type=device.device_type,
        role=device.role,
        device_family=device.device_family,
        display_name=device.display_name,
        default_config=device.default_config,
        zone_id=getattr(device, "zone_id", None),
        location_id=getattr(device, "location_id", None),
    )


def devices_to_dtos(
    devices: list[Device],
) -> list[DeviceDto]:
    return [
        device_to_dto(device)
        for device in devices
    ]


def get_device_service(
    db: Session = Depends(get_db),
) -> DeviceFamilyService:
    repository = DeviceRepository(db)
    return DeviceFamilyService(repository)


@router.get(
    "",
    response_model=list[DeviceDto],
)
def list_devices(
    family: str | None = Query(default=None),
    role: str | None = Query(default=None),
    service: DeviceFamilyService = Depends(get_device_service),
) -> list[DeviceDto]:
    devices = service.list_devices(
        device_family=family,
        role=role,
    )

    return devices_to_dtos(devices)


@router.post(
    "/provision",
    response_model=list[DeviceDto],
    status_code=status.HTTP_201_CREATED,
)
def provision_devices(
    family: str = Query(...),
    service: DeviceFamilyService = Depends(get_device_service),
) -> list[DeviceDto]:
    try:
        get_family_factory(family)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown device family: {family}",
        )

    devices = service.provision_family(family)

    return devices_to_dtos(devices)


@router.patch(
    "/{device_id}/zone",
    status_code=status.HTTP_204_NO_CONTENT,
)
def assign_device_to_zone(
    device_id: UUID,
    request: ZoneAssignmentRequestDto,
    db: Session = Depends(get_db),
):
    service = ZoneAssignmentService(db)

    try:
        service.assign(
            device_id=device_id,
            zone_id=request.zone_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc