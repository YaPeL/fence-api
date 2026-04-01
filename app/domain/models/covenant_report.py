from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class CovenantStatus(StrEnum):
    COMPLIANT = "COMPLIANT"
    BREACH = "BREACH"


@dataclass(frozen=True, slots=True)
class ExcludedAsset:
    external_id: str
    reasons: list[str]


@dataclass(frozen=True, slots=True)
class CovenantReportSummary:
    total_assets_evaluated: int
    assets_included: int
    assets_excluded: int


@dataclass(frozen=True, slots=True)
class CovenantReport:
    facility: str
    effective_rate_percentage: Decimal
    covenant_status: CovenantStatus
    summary: CovenantReportSummary
    included_assets: list[str]
    excluded_assets: list[ExcludedAsset]
