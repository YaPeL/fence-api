from __future__ import annotations

from typing import Any

from app.core.normalizers.base import normalize_status, to_bool, to_decimal
from app.domain.models import EducaAsset


def normalize_educa_assets(raw_assets: list[dict[str, Any]]) -> list[EducaAsset]:
    normalized_assets: list[EducaAsset] = []

    for raw_asset in raw_assets:
        normalized_assets.append(
            EducaAsset(
                external_id=str(raw_asset.get("external_id", "")),
                status=normalize_status(raw_asset.get("status")),
                is_eligible=to_bool(raw_asset.get("is_eligible")),
                loan_status=normalize_status(raw_asset.get("loan_status")),
                interest_rate_percentage=to_decimal(raw_asset.get("interest_rate_percentage")),
                outstanding_amount=to_decimal(raw_asset.get("outstanding_amount")),
            )
        )

    return normalized_assets
