from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class NominaAsset:
    external_id: str
    status: str
    is_eligible: bool
    outstanding_amount: Decimal | None
    fee_percentage: Decimal | None
    origination_date: date | None
    maturity_date: date | None
