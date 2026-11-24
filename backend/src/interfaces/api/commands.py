from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from application.commands.dto import CommandLogDto, CommandRequestDto
from application.commands.service import CommandService
from infrastructure.db import get_db
from composition import get_event_bus
from domain.events.bus import EventBus


router = APIRouter(
    prefix="/api/commands",
    tags=["commands"],
)


@router.post(
    "",
    response_model=CommandLogDto,
    responses={
        status.HTTP_409_CONFLICT: {
            "model": CommandLogDto,
            "description": "Rejected: command not allowed in current state.",
        },
    },
)
def submit_command(
    request: CommandRequestDto,
    response: Response,
    db: Session = Depends(get_db),
    bus: EventBus = Depends(get_event_bus),
) -> CommandLogDto:
    try:
        log = CommandService(db, bus=bus).submit(
            request.command_type,
            request.device_id,
            request.payload,
        )

    except LookupError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    if log.status == "rejected":
        response.status_code = status.HTTP_409_CONFLICT

    return log


@router.get("", response_model=list[CommandLogDto])
def list_commands(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[CommandLogDto]:
    return CommandService(db).list_recent(limit)
