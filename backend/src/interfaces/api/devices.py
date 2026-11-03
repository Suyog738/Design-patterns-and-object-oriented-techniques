from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from application.devices.service import DeviceFamilyService
from application.locations.dto import ZoneAssignmentRequestDto
from application.locations.zone_assignment_service import (
    ZoneAssignmentService,
)
from domain.actuators.state import (
    ActuatorState,
    IllegalTransitionError,
    get_allowed_commands,
)
from domain.devices.entity import Device
from domain.devices.factories import get_family_factory
from infrastructure.db import get_db
from infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)
from infrastructure.persistence.device_repository import DeviceRepository
from infrastructure.persistence.models import DeviceRow


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
    state: str | None = None
    allowed_commands: list[str] = Field(default_factory=list)


class SamplingUpdateRequest(BaseModel):
    sampling_interval_seconds: int
    tracking_enabled: bool


class TransitionRequest(BaseModel):
    target: str


def device_to_dto(
    device: Device,
    state: str | None = None,
) -> DeviceDto:
    if device.id is None:
        raise ValueError(
            "Device must be saved before converting to DTO"
        )

    allowed_commands = (
        get_allowed_commands(ActuatorState(state))
        if device.role == "actuator" and state is not None
        else []
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
        state=state,
        allowed_commands=allowed_commands,
    )


def devices_to_dtos(
    devices: list[Device],
    state_repository: ActuatorStateRepository,
) -> list[DeviceDto]:
    states = state_repository.get_states(
        [
            device.id
            for device in devices
            if device.role == "actuator" and device.id is not None
        ]
    )

    return [
        device_to_dto(
            device,
            states.get(device.id) if device.role == "actuator" else None,
        )
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
    db: Session = Depends(get_db),
) -> list[DeviceDto]:
    devices = service.list_devices(
        device_family=family,
        role=role,
    )

    return devices_to_dtos(
        devices,
        ActuatorStateRepository(db),
    )


@router.post(
    "/provision",
    response_model=list[DeviceDto],
    status_code=status.HTTP_201_CREATED,
)
def provision_devices(
    family: str = Query(...),
    service: DeviceFamilyService = Depends(get_device_service),
    db: Session = Depends(get_db),
) -> list[DeviceDto]:
    try:
        get_family_factory(family)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown device family: {family}",
        )

    devices = service.provision_family(family)

    return devices_to_dtos(
        devices,
        ActuatorStateRepository(db),
    )


@router.post(
    "/{device_id}/transition",
    response_model=DeviceDto,
)
def transition_actuator(
    device_id: UUID,
    request: TransitionRequest,
    db: Session = Depends(get_db),
) -> DeviceDto:
    repository = ActuatorStateRepository(db)

    try:
        state, _ = repository.transition(
            device_id=device_id,
            target=request.target,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except IllegalTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    device_row = db.get(DeviceRow, device_id)

    if device_row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found.",
        )

    device = Device(
        id=device_row.id,
        device_type=device_row.device_type,
        role=device_row.role,
        device_family=device_row.device_family,
        display_name=device_row.display_name or "",
        default_config=device_row.default_config or {},
        zone_id=device_row.zone_id,
        location_id=device_row.location_id,
    )

    return device_to_dto(
        device,
        state.value,
    )


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


@router.patch(
    "/{device_id}/sampling",
    response_model=DeviceDto,
)
def update_sampling(
    device_id: UUID,
    request: SamplingUpdateRequest,
    db: Session = Depends(get_db),
) -> DeviceDto:
    if request.sampling_interval_seconds < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sampling_interval_seconds must be at least 5.",
        )

    device = db.get(
        DeviceRow,
        device_id,
    )

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found.",
        )

    if device.role != "sensor":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sampling settings can only be changed for sensors.",
        )

    device.sampling_interval_seconds = (
        request.sampling_interval_seconds
    )
    device.tracking_enabled = request.tracking_enabled

    db.commit()
    db.refresh(device)

    domain_device = Device(
        id=device.id,
        device_type=device.device_type,
        role=device.role,
        device_family=device.device_family,
        display_name=device.display_name or "",
        default_config=device.default_config or {},
        zone_id=device.zone_id,
        location_id=device.location_id,
    )

    return device_to_dto(domain_device)