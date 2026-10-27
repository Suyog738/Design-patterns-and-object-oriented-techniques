from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from application.overview.dto import LocationOverviewDto
from application.overview.facade import LocationOverviewFacade
from infrastructure.db import get_db


router = APIRouter(
    prefix="/api/locations",
    tags=["Overview"],
)


def get_location_overview_facade(
    db: Session = Depends(get_db),
) -> LocationOverviewFacade:
    return LocationOverviewFacade(db)


@router.get(
    "/{location_id}/overview",
    response_model=LocationOverviewDto,
)
def get_location_overview(
    location_id: UUID,
    facade: LocationOverviewFacade = Depends(
        get_location_overview_facade
    ),
) -> LocationOverviewDto:
    try:
        return facade.get_overview(location_id)
    except ValueError as error:
        if str(error) == "Location not found.":
            raise HTTPException(
                status_code=404,
                detail=str(error),
            ) from error

        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
  