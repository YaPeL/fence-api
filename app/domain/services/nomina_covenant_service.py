from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from app.domain.models import CovenantReport, CovenantReportSummary, CovenantStatus, ExcludedAsset, NominaAsset

_NOMINA_THRESHOLD = Decimal("5.0")


def _is_end_of_month(value: date) -> bool:
    return (value + timedelta(days=1)).day == 1


def _repayment_months(asset: NominaAsset) -> int | None:
    if asset.origination_date is None or asset.maturity_date is None:
        return None

    months = (asset.maturity_date.year - asset.origination_date.year) * 12 + (
        asset.maturity_date.month - asset.origination_date.month
    )
    if asset.maturity_date.day < asset.origination_date.day and not (
        _is_end_of_month(asset.origination_date) and _is_end_of_month(asset.maturity_date)
    ):
        months -= 1

    return months if months > 0 else None


def calculate_nomina_covenant_report(assets: list[NominaAsset]) -> CovenantReport:
    included_assets: list[str] = []
    excluded_assets: list[ExcludedAsset] = []

    weighted_sum = Decimal("0")
    total_outstanding = Decimal("0")

    for asset in assets:
        reasons: list[str] = []

        if asset.status != "active":
            reasons.append("status mismatch")
        if not asset.is_eligible:
            reasons.append("ineligible flag")
        if asset.outstanding_amount is None or asset.outstanding_amount <= 0:
            reasons.append("outstanding_amount must be > 0")

        repayment_months = _repayment_months(asset)
        if repayment_months is None:
            reasons.append("invalid origination_date or maturity_date")

        if asset.fee_percentage is None:
            reasons.append("missing fee_percentage")

        if reasons:
            excluded_assets.append(ExcludedAsset(external_id=asset.external_id, reasons=reasons))
            continue

        assert asset.outstanding_amount is not None
        assert asset.fee_percentage is not None
        assert repayment_months is not None

        annualized_fee = asset.fee_percentage * (Decimal("12") / Decimal(repayment_months))
        included_assets.append(asset.external_id)
        weighted_sum += asset.outstanding_amount * annualized_fee
        total_outstanding += asset.outstanding_amount

    effective_rate = Decimal("0")
    covenant_status = CovenantStatus.BREACH

    if total_outstanding > 0:
        effective_rate = weighted_sum / total_outstanding
        covenant_status = CovenantStatus.BREACH if effective_rate >= _NOMINA_THRESHOLD else CovenantStatus.COMPLIANT

    summary = CovenantReportSummary(
        total_assets_evaluated=len(assets),
        assets_included=len(included_assets),
        assets_excluded=len(excluded_assets),
    )

    return CovenantReport(
        facility="nomina",
        effective_rate_percentage=effective_rate,
        covenant_status=covenant_status,
        summary=summary,
        included_assets=included_assets,
        excluded_assets=excluded_assets,
    )
