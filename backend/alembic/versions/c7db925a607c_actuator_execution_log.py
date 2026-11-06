"""actuator_execution_log

Revision ID: c7db925a607c
Revises: cba2941432dc
Create Date: 2026-11-04 12:16:28.398236
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c7db925a607c'
down_revision: Union[str, Sequence[str], None] = 'cba2941432dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "actuator_execution_log",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("device_id", sa.UUID(), nullable=False),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column(
            "policy_applied",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["devices.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_actuator_execution_log_device_id"),
        "actuator_execution_log",
        ["device_id"],
    )
    op.create_index(
        op.f("ix_actuator_execution_log_created_at"),
        "actuator_execution_log",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_actuator_execution_log_created_at"),
        table_name="actuator_execution_log",
    )
    op.drop_index(
        op.f("ix_actuator_execution_log_device_id"),
        table_name="actuator_execution_log",
    )
    op.drop_table("actuator_execution_log")


    op.create_table('automation_rules',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), autoincrement=False, nullable=False),
    sa.Column('location_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('strategy_key', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
    sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['location_id'], ['locations.id'], name=op.f('automation_rules_location_id_fkey'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('automation_rules_pkey')),
    sa.UniqueConstraint('location_id', name=op.f('automation_rules_location_id_key'), postgresql_include=[], postgresql_nulls_not_distinct=False)
    )
    op.create_table('sensor_readings',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), autoincrement=False, nullable=False),
    sa.Column('device_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('value', sa.NUMERIC(precision=10, scale=4), autoincrement=False, nullable=False),
    sa.Column('unit', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
    sa.Column('source', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
    sa.Column('recorded_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['device_id'], ['devices.id'], name=op.f('sensor_readings_device_id_fkey'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('sensor_readings_pkey'))
    )
    op.create_index(op.f('ix_sensor_readings_device_recorded_at'), 'sensor_readings', ['device_id', 'recorded_at'], unique=False)
    op.create_table('actuator_states',
    sa.Column('device_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('state', sa.VARCHAR(length=20), server_default=sa.text("'idle'::character varying"), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['device_id'], ['devices.id'], name=op.f('actuator_states_device_id_fkey'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('device_id', name=op.f('actuator_states_pkey'))
    )
    op.create_table('zones',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), autoincrement=False, nullable=False),
    sa.Column('location_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=128), autoincrement=False, nullable=False),
    sa.Column('moisture_threshold_low', sa.NUMERIC(), autoincrement=False, nullable=False),
    sa.Column('moisture_threshold_high', sa.NUMERIC(), autoincrement=False, nullable=False),
    sa.Column('schedule', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['location_id'], ['locations.id'], name=op.f('zones_location_id_fkey'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('zones_pkey'))
    )
    op.create_index(op.f('ix_zones_location_id'), 'zones', ['location_id'], unique=False)
    op.create_table('devices',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), autoincrement=False, nullable=False),
    sa.Column('device_type', sa.VARCHAR(length=64), autoincrement=False, nullable=False),
    sa.Column('role', sa.VARCHAR(length=32), server_default=sa.text("'sensor'::character varying"), autoincrement=False, nullable=False),
    sa.Column('display_name', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.Column('default_config', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('device_family', sa.VARCHAR(length=32), server_default=sa.text("'simulation'::character varying"), autoincrement=False, nullable=False),
    sa.Column('location_id', sa.UUID(), autoincrement=False, nullable=True),
    sa.Column('zone_id', sa.UUID(), autoincrement=False, nullable=True),
    sa.Column('sampling_interval_seconds', sa.INTEGER(), server_default=sa.text('300'), autoincrement=False, nullable=False),
    sa.Column('tracking_enabled', sa.BOOLEAN(), server_default=sa.text('true'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['location_id'], ['locations.id'], name=op.f('fk_devices_location_id_locations'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['zone_id'], ['zones.id'], name=op.f('fk_devices_zone_id_zones'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('devices_pkey'))
    )
    op.create_index(op.f('ix_devices_zone_id'), 'devices', ['zone_id'], unique=False)
    op.create_index(op.f('ix_devices_role'), 'devices', ['role'], unique=False)
    op.create_index(op.f('ix_devices_location_id'), 'devices', ['location_id'], unique=False)
    op.create_index(op.f('ix_devices_family'), 'devices', ['device_family'], unique=False)
    op.create_table('locations',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=128), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('locations_pkey'))
    )
    # ### end Alembic commands ###