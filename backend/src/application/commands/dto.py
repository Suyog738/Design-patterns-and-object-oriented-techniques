from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CommandRequestDto(BaseModel):
    command_type: str
    device_id: UUID
    payload: dict = Field(default_factory=dict)


class CommandLogDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    command_type: str
    device_id: UUID
    payload: dict
    status: Literal["success", "failed", "rejected"]
    error_message: str | None = None
    created_at: datetime
