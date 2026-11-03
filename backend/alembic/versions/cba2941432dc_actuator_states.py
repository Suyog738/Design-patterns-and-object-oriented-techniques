"""actuator_states

Revision ID: cba2941432dc
Revises: f5338dc0387b
Create Date: 2026-11-03 12:37:46.540259
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "cba2941432dc"
down_revision: Union[str, Sequence[str], None] = "f5338dc0387b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "actuator_states",
        sa.Column("device_id", sa.UUID(), nullable=False),
        sa.Column(
            "state",
            sa.String(length=20),
            nullable=False,
            server_default="idle",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["devices.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("device_id"),
    )

    # Initialize existing actuators as idle.
    op.execute(
        sa.text(
            """
            INSERT INTO actuator_states (device_id, state)
            SELECT id, 'idle'
            FROM devices
            WHERE role = 'actuator'
            ON CONFLICT (device_id) DO NOTHING
            """
        )
    )


def downgrade() -> None:
    op.drop_table("actuator_states")
