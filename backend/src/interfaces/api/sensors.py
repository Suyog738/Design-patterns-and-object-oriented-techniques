from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from application.readings.dto import ReadingDto
from application.readings.service import ReadingIngest
from application.sensors.service import SensorService
from infrastructure.db import get_db
from infrastructure.persistence.device_repository import DeviceRepository


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


def get_reading_ingest(
    db: Session = Depends(get_db),
) -> ReadingIngest:
    return ReadingIngest(db)


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


@router.post(
    "/{device_id}/read",
    response_model=ReadingDto,
)
def read_sensor(
    device_id: UUID,
    service: ReadingIngest = Depends(get_reading_ingest),
):
    try:
        return service.take_reading(device_id)

    except ValueError as exc:
        message = str(exc)

        if message == "Device not found.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


@router.get(
    "/{device_id}/readings",
    response_model=list[ReadingDto],
)
def get_sensor_readings(
    device_id: UUID,
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    service: ReadingIngest = Depends(get_reading_ingest),
):
    try:
        return service.list_readings(
            device_id,
            limit,
        )

    except ValueError as exc:
        message = str(exc)

        if message == "Device not found.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )