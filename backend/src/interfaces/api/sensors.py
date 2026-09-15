from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from application.sensors.service import SensorService
from infrastructure.persistence.device_repository import DeviceRepository
from infrastructure.db import get_db


router = APIRouter(
    prefix="/api/sensors",
    tags=["sensors"],
)


class SensorCreateRequest(BaseModel):
    type: str
    display_name: str | None = None


class SensorResponse(BaseModel):
    id: UUID
    device_type: str
    display_name: str | None
    default_config: dict


def get_sensor_service(
    db: Session = Depends(get_db),
) -> SensorService:
    repository = DeviceRepository(db)
    return SensorService(repository)


@router.post(
    "",
    response_model=SensorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sensor(
    request: SensorCreateRequest,
    service: SensorService = Depends(get_sensor_service),
):
    try:
        sensor = service.create_sensor(
            sensor_type=request.type,
            display_name=request.display_name,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    return SensorResponse(
        id=sensor.id,
        device_type=sensor.device_type,
        display_name=sensor.display_name,
        default_config=sensor.default_config,
    )


@router.get(
    "",
    response_model=list[SensorResponse],
)
def list_sensors(
    service: SensorService = Depends(get_sensor_service),
):
    sensors = service.list_sensors()

    return [
        SensorResponse(
            id=sensor.id,
            device_type=sensor.device_type,
            display_name=sensor.display_name,
            default_config=sensor.default_config,
        )
        for sensor in sensors
    ]