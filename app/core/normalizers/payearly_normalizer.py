from __future__ import annotations

from datetime import date, datetime
from typing import Any

from app.core.normalizers.base import normalize_status, to_bool, to_decimal
from app.domain.models import PayEarlyAsset

_PAYEARLY_DATE_FORMATS = ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ")


def parse_payearly_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    if not isinstance(value, str):
        return None

    clean_value = value.strip()
    if not clean_value:
        return None

    for fmt in _PAYEARLY_DATE_FORMATS:
        try:
            parsed = datetime.strptime(clean_value, fmt)
            if fmt == "%Y-%m-%d":
                return datetime.combine(parsed.date(), datetime.min.time())
            return parsed
        except ValueError:
            continue
    return None


def normalize_payearly_assets(raw_assets: list[dict[str, Any]]) -> list[PayEarlyAsset]:
    normalized_assets: list[PayEarlyAsset] = []

    for raw_asset in raw_assets:
        normalized_assets.append(
            PayEarlyAsset(
                external_id=str(raw_asset.get("external_id", "")),
                status=normalize_status(raw_asset.get("status")),
                is_eligible=to_bool(raw_asset.get("is_eligible")),
                outstanding_principal_amount=to_decimal(raw_asset.get("outstanding_principal_amount")),
                total_fee_amount=to_decimal(raw_asset.get("total_fee_amount")),
                total_principal_amount=to_decimal(raw_asset.get("total_principal_amount")),
                created_at=parse_payearly_datetime(raw_asset.get("created_at")),
                due_date=parse_payearly_datetime(raw_asset.get("due_date")),
            )
        )

    return normalized_assets
