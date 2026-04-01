from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import DateTime, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import Base


class PublishedCovenantReportModel(Base):
    __tablename__ = "published_covenant_reports"
    __table_args__ = (
        UniqueConstraint(
            "facility",
            "calculation_version",
            "normalized_payload_hash",
            name="uq_published_covenant_reports_facility_version_payload_hash",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    facility: Mapped[str] = mapped_column(String(50), nullable=False)
    calculation_version: Mapped[str] = mapped_column(String(20), nullable=False)
    normalized_payload_json: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False)
    normalized_payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    effective_rate_percentage: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    threshold_percentage: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    covenant_status: Mapped[str] = mapped_column(String(20), nullable=False)
    total_assets_evaluated: Mapped[int] = mapped_column(Integer, nullable=False)
    assets_included_count: Mapped[int] = mapped_column(Integer, nullable=False)
    assets_excluded_count: Mapped[int] = mapped_column(Integer, nullable=False)
    included_assets: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    excluded_assets: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
