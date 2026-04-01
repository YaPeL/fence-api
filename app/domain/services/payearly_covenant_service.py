from __future__ import annotations

from decimal import Decimal

from app.domain.models import CovenantReport, CovenantReportSummary, CovenantStatus, ExcludedAsset, PayEarlyAsset

_PAYEARLY_THRESHOLD = Decimal("3.0")
_DAYS_IN_YEAR = Decimal("365")
_PERCENT_MULTIPLIER = Decimal("100")
_SECONDS_IN_DAY = Decimal("86400")
_MICROSECONDS_IN_SECOND = Decimal("1000000")


def calculate_payearly_covenant_report(assets: list[PayEarlyAsset]) -> CovenantReport:
    included_assets: list[str] = []
    excluded_assets: list[ExcludedAsset] = []

    weighted_sum = Decimal("0")
    total_outstanding = Decimal("0")

    for asset in assets:
        reasons: list[str] = []

        if asset.status != "performing":
            reasons.append("status mismatch")
        if not asset.is_eligible:
            reasons.append("ineligible flag")
        if asset.outstanding_principal_amount is None or asset.outstanding_principal_amount <= 0:
            reasons.append("outstanding_principal_amount must be > 0")

        tenor_days = None
        if asset.created_at is None or asset.due_date is None:
            reasons.append("invalid created_at or due_date")
        else:
            tenor_delta = asset.due_date - asset.created_at
            tenor_seconds = Decimal(tenor_delta.days * 86400 + tenor_delta.seconds) + (
                Decimal(tenor_delta.microseconds) / _MICROSECONDS_IN_SECOND
            )
            tenor_days = tenor_seconds / _SECONDS_IN_DAY
            if tenor_days <= 0:
                reasons.append("invalid created_at or due_date")

        if asset.total_principal_amount is None or asset.total_principal_amount <= 0:
            reasons.append("total_principal_amount must be > 0")
        if asset.total_fee_amount is None:
            reasons.append("missing total_fee_amount")

        if reasons:
            excluded_assets.append(ExcludedAsset(external_id=asset.external_id, reasons=reasons))
            continue

        assert asset.outstanding_principal_amount is not None
        assert asset.total_principal_amount is not None
        assert asset.total_fee_amount is not None
        assert tenor_days is not None

        fee_yield = (
            (asset.total_fee_amount / asset.total_principal_amount) * (_DAYS_IN_YEAR / tenor_days) * _PERCENT_MULTIPLIER
        )
        included_assets.append(asset.external_id)
        weighted_sum += asset.outstanding_principal_amount * fee_yield
        total_outstanding += asset.outstanding_principal_amount

    effective_rate = Decimal("0")
    covenant_status = CovenantStatus.BREACH

    if total_outstanding > 0:
        effective_rate = weighted_sum / total_outstanding
        covenant_status = CovenantStatus.BREACH if effective_rate >= _PAYEARLY_THRESHOLD else CovenantStatus.COMPLIANT

    summary = CovenantReportSummary(
        total_assets_evaluated=len(assets),
        assets_included=len(included_assets),
        assets_excluded=len(excluded_assets),
    )

    return CovenantReport(
        facility="payearly",
        effective_rate_percentage=effective_rate,
        covenant_status=covenant_status,
        summary=summary,
        included_assets=included_assets,
        excluded_assets=excluded_assets,
    )
