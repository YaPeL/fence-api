from __future__ import annotations

from decimal import Decimal

from app.domain.models import CovenantReport, CovenantReportSummary, CovenantStatus, EducaAsset, ExcludedAsset

_EDUCA_THRESHOLD = Decimal("22.0")
_REASON_STATUS_MISMATCH = "status mismatch"
_REASON_INELIGIBLE_FLAG = "ineligible flag"
_REASON_LOAN_STATUS_MISMATCH = "loan_status mismatch"
_REASON_MISSING_INTEREST_RATE = "missing interest_rate_percentage"
_REASON_MISSING_OUTSTANDING_AMOUNT = "missing outstanding_amount"
_REASON_NEGATIVE_OUTSTANDING_AMOUNT = "outstanding_amount must be >= 0"


def calculate_educa_covenant_report(assets: list[EducaAsset]) -> CovenantReport:
    included_assets: list[str] = []
    excluded_assets: list[ExcludedAsset] = []

    weighted_sum = Decimal("0")
    total_outstanding = Decimal("0")

    for asset in assets:
        reasons: list[str] = []

        if asset.status != "open":
            reasons.append(_REASON_STATUS_MISMATCH)
        if not asset.is_eligible:
            reasons.append(_REASON_INELIGIBLE_FLAG)
        if asset.loan_status != "current":
            reasons.append(_REASON_LOAN_STATUS_MISMATCH)
        if asset.interest_rate_percentage is None:
            reasons.append(_REASON_MISSING_INTEREST_RATE)
        if asset.outstanding_amount is None:
            reasons.append(_REASON_MISSING_OUTSTANDING_AMOUNT)
        elif asset.outstanding_amount < 0:
            reasons.append(_REASON_NEGATIVE_OUTSTANDING_AMOUNT)

        if reasons:
            excluded_assets.append(ExcludedAsset(external_id=asset.external_id, reasons=reasons))
            continue

        assert asset.interest_rate_percentage is not None
        assert asset.outstanding_amount is not None
        included_assets.append(asset.external_id)
        weighted_sum += asset.outstanding_amount * asset.interest_rate_percentage
        total_outstanding += asset.outstanding_amount

    # Task behavior: no eligible assets => rate 0.00 and BREACH (conservative default).
    effective_rate = Decimal("0")
    covenant_status = CovenantStatus.BREACH

    if included_assets:
        if total_outstanding > 0:
            effective_rate = weighted_sum / total_outstanding
        covenant_status = CovenantStatus.BREACH if effective_rate >= _EDUCA_THRESHOLD else CovenantStatus.COMPLIANT

    summary = CovenantReportSummary(
        total_assets_evaluated=len(assets),
        assets_included=len(included_assets),
        assets_excluded=len(excluded_assets),
    )

    return CovenantReport(
        facility="educa",
        effective_rate_percentage=effective_rate,
        covenant_status=covenant_status,
        summary=summary,
        included_assets=included_assets,
        excluded_assets=excluded_assets,
    )
