from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Numeric,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.persistence.base import Base


class DeviceRow(Base):
    __tablename__ = "devices"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    device_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    device_family: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        server_default="simulation",
        index=True,
    )

    display_name: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    default_config: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    zone_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "zones.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    location_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "locations.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )


class LocationRow(Base):
    __tablename__ = "locations"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    zones: Mapped[list["ZoneRow"]] = relationship(
        "ZoneRow",
        back_populates="location",
        cascade="all, delete-orphan",
    )


class ZoneRow(Base):
    __tablename__ = "zones"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    location_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "locations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    moisture_threshold_low: Mapped[float] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )

    moisture_threshold_high: Mapped[float] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )

    schedule: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    location: Mapped["LocationRow"] = relationship(
        "LocationRow",
        back_populates="zones",
    )