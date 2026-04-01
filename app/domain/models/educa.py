from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class EducaAsset:
    external_id: str
    status: str
    is_eligible: bool
    loan_status: str
    interest_rate_percentage: Decimal | None
    outstanding_amount: Decimal | None
