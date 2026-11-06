from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from application.actuators.dto import ActuatorExecutionDto
from application.actuators.service import ActuatorService
from domain.actuators.ports import ActuatorPolicyError
from infrastructure.db import get_db


router = APIRouter(
    prefix="/api/actuators",
    tags=["actuators"],
)


class ApplyCommandRequest(BaseModel):
    command: str
    payload: dict = Field(default_factory=dict)


@router.get(
    "/executions",
    response_model=list[ActuatorExecutionDto],
)
def list_executions(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[ActuatorExecutionDto]:
    return ActuatorService(db).list_executions(limit)


# Demo endpoint until Phase 10 (Command).
@router.post(
    "/{device_id}/apply",
    status_code=status.HTTP_204_NO_CONTENT,
)
def apply_command(
    device_id: UUID,
    request: ApplyCommandRequest,
    db: Session = Depends(get_db),
):
    service = ActuatorService(db)

    try:
        service.apply(
            device_id,
            request.command,
            request.payload,
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
    except ActuatorPolicyError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
