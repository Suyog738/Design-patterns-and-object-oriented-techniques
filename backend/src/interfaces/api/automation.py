
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from application.automation.service import AutomationService
from infrastructure.db import get_db

router = APIRouter(
    prefix="/api/locations/{location_id}/automation",
    tags=["Automation"],
)


class StrategyRequest(BaseModel):
    strategy_key: str


@router.put("")
def set_strategy(
    location_id: UUID,
    request: StrategyRequest,
    db: Session = Depends(get_db),
):
    service = AutomationService(db)

    try:
        service.set_strategy(
            location_id,
            request.strategy_key,
        )
    except ValueError as error:
        message = str(error)

        if message == "Location not found.":
            raise HTTPException(
                status_code=404,
                detail=message,
            )

        raise HTTPException(
            status_code=400,
            detail=message,
        )

    return {
        "location_id": location_id,
        "strategy_key": request.strategy_key,
    }


@router.post("/evaluate")
def evaluate_automation(
    location_id: UUID,
    db: Session = Depends(get_db),
):
    service = AutomationService(db)

    try:
        return service.evaluate(location_id)
    except ValueError as error:
        message = str(error)

        if message == "Location not found.":
            raise HTTPException(
                status_code=404,
                detail=message,
            )

        raise HTTPException(
            status_code=400,
            detail=message,
        )
