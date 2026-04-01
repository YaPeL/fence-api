from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.domain.models.covenant_report import CovenantStatus


@dataclass(frozen=True, slots=True)
class PublishCovenantReportCommand:
    facility: str
    calculation_version: str
    normalized_payload_json: list[dict[str, Any]]
    normalized_payload_hash: str
    effective_rate_percentage: Decimal
    threshold_percentage: Decimal
    covenant_status: CovenantStatus
    total_assets_evaluated: int
    assets_included_count: int
    assets_excluded_count: int
    included_assets: list[str]
    excluded_assets: list[dict[str, Any]]


@dataclass(frozen=True, slots=True)
class CovenantReportPublication:
    id: int
    calculation_version: str
    normalized_payload_hash: str
    published_at: datetime
    was_already_published: bool
