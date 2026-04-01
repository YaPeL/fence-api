from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import Any

from app.application.ports import CovenantReportPublisher
from app.core.db.hashing import hash_normalized_payload, normalized_assets_to_json
from app.core.normalizers import normalize_payearly_assets
from app.domain.models import CovenantReport, PublishCovenantReportCommand
from app.domain.services import calculate_payearly_covenant_report

CALCULATION_VERSION = "v1"
PAYEARLY_THRESHOLD_PERCENTAGE = Decimal("3.0")


def generate_payearly_covenant_report(raw_assets: list[dict[str, Any]]) -> CovenantReport:
    assets = normalize_payearly_assets(raw_assets)
    return calculate_payearly_covenant_report(assets)


async def generate_and_publish_payearly_covenant_report(
    raw_assets: list[dict[str, Any]],
    publisher: CovenantReportPublisher,
) -> CovenantReport:
    assets = normalize_payearly_assets(raw_assets)
    report = calculate_payearly_covenant_report(assets)

    normalized_payload_json = normalized_assets_to_json(assets)
    normalized_payload_hash = hash_normalized_payload(normalized_payload_json)
    publication = await publisher.publish(
        PublishCovenantReportCommand(
            facility=report.facility,
            calculation_version=CALCULATION_VERSION,
            normalized_payload_json=normalized_payload_json,
            normalized_payload_hash=normalized_payload_hash,
            effective_rate_percentage=report.effective_rate_percentage,
            threshold_percentage=PAYEARLY_THRESHOLD_PERCENTAGE,
            covenant_status=report.covenant_status,
            total_assets_evaluated=report.summary.total_assets_evaluated,
            assets_included_count=report.summary.assets_included,
            assets_excluded_count=report.summary.assets_excluded,
            included_assets=report.included_assets,
            excluded_assets=[
                {"external_id": excluded.external_id, "reasons": excluded.reasons}
                for excluded in report.excluded_assets
            ],
        )
    )

    return replace(report, publication=publication)
