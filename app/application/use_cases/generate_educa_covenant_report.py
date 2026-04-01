from __future__ import annotations

from typing import Any

from app.core.normalizers import normalize_educa_assets
from app.domain.models import CovenantReport
from app.domain.services import calculate_educa_covenant_report


def generate_educa_covenant_report(raw_assets: list[dict[str, Any]]) -> CovenantReport:
    assets = normalize_educa_assets(raw_assets)
    return calculate_educa_covenant_report(assets)
