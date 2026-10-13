"""automation_rules

Revision ID: f5338dc0387b
Revises: 79bc9ac36149
Create Date: 2026-10-07 13:25:08.712893
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'f5338dc0387b'
down_revision: Union[str, Sequence[str], None] = '79bc9ac36149'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'automation_rules',
        sa.Column(
            'id',
            sa.UUID(),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False
        ),
        sa.Column(
            'location_id',
            sa.UUID(),
            nullable=False
        ),
        sa.Column(
            'strategy_key',
            sa.String(length=32),
            nullable=False
        ),
        sa.Column(
            'parameters',
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False
        ),
        sa.Column(
            'updated_at',
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ['location_id'],
            ['locations.id'],
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('location_id')
    )


def downgrade() -> None:
    op.drop_table('automation_rules')

