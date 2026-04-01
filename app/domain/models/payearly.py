from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class PayEarlyAsset:
    external_id: str
    status: str
    is_eligible: bool
    outstanding_principal_amount: Decimal | None
    total_fee_amount: Decimal | None
    total_principal_amount: Decimal | None
    created_at: datetime | None
    due_date: datetime | None
