from uuid import UUID

from pydantic import BaseModel


class RecommendationDto(BaseModel):
    location_id: UUID
    strategy_key: str
    action: str
    reason: str
    score: float | None = None