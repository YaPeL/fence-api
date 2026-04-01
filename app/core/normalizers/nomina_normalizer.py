from __future__ import annotations

from typing import Any

from app.core.normalizers.base import normalize_status, parse_date, to_bool, to_decimal
from app.domain.models import NominaAsset

_NOMINA_DATE_FORMATS = ("%d/%m/%Y", "%Y-%m-%d")


def normalize_nomina_assets(raw_assets: list[dict[str, Any]]) -> list[NominaAsset]:
    normalized_assets: list[NominaAsset] = []

    for raw_asset in raw_assets:
        normalized_assets.append(
            NominaAsset(
                external_id=str(raw_asset.get("external_id", "")),
                status=normalize_status(raw_asset.get("status")),
                is_eligible=to_bool(raw_asset.get("is_eligible")),
                outstanding_amount=to_decimal(raw_asset.get("outstanding_amount")),
                fee_percentage=to_decimal(raw_asset.get("fee_percentage")),
                origination_date=parse_date(raw_asset.get("origination_date"), _NOMINA_DATE_FORMATS),
                maturity_date=parse_date(raw_asset.get("maturity_date"), _NOMINA_DATE_FORMATS),
            )
        )

    return normalized_assets
