from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from application.alerts.dto import AlertDto
from infrastructure.db import get_db
from infrastructure.persistence.alert_repository import AlertRepository


router = APIRouter(
    prefix="/api/alerts",
    tags=["alerts"],
)

ALERT_STATUSES = {"active", "resolved", "all"}


@router.get("", response_model=list[AlertDto])
def list_alerts(
    status_filter: str = Query(default="active", alias="status"),
    location_id: UUID | None = Query(default=None),
    zone_id: UUID | None = Query(default=None),
    since: datetime | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[AlertDto]:
    if status_filter not in ALERT_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="status must be one of: active, resolved, all.",
        )

    rows = AlertRepository(db).list_alerts(
        status=status_filter,
        location_id=location_id,
        zone_id=zone_id,
        since=since,
        limit=limit,
    )

    return [AlertDto.model_validate(row) for row in rows]
