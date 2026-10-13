from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.persistence.models import AutomationRuleRow


class AutomationRepository:
    def __init__(self, db: Session):
        self._db = db

    def set_strategy(
        self,
        location_id: UUID,
        strategy_key: str,
    ) -> None:
        statement = (
            select(AutomationRuleRow)
            .where(
                AutomationRuleRow.location_id == location_id
            )
        )

        row = self._db.scalar(statement)

        if row is None:
            row = AutomationRuleRow(
                location_id=location_id,
                strategy_key=strategy_key,
                parameters={},
            )
            self._db.add(row)
        else:
            row.strategy_key = strategy_key
            row.updated_at = datetime.now(timezone.utc)

        self._db.commit()

    def get_strategy(
        self,
        location_id: UUID,
    ) -> str | None:
        statement = (
            select(AutomationRuleRow.strategy_key)
            .where(
                AutomationRuleRow.location_id == location_id
            )
        )

        return self._db.scalar(statement)