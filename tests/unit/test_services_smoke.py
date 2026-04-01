from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from app.application.use_cases import (
    generate_educa_covenant_report,
    generate_nomina_covenant_report,
    generate_payearly_covenant_report,
)
from app.core.normalizers.base import to_decimal
from app.core.normalizers.payearly_normalizer import normalize_payearly_assets
from app.domain.models import CovenantStatus
from app.main import app


@pytest.mark.smoke
def test_educa_happy_path_service() -> None:
    report = generate_educa_covenant_report(
        [
            {
                "external_id": "E-1",
                "status": "open",
                "is_eligible": True,
                "loan_status": "current",
                "interest_rate_percentage": "21.5",
                "outstanding_amount": "1000",
            },
            {
                "external_id": "E-2",
                "status": "open",
                "is_eligible": True,
                "loan_status": "current",
                "interest_rate_percentage": "20.0",
                "outstanding_amount": "500",
            },
        ]
    )

    assert report.covenant_status == CovenantStatus.COMPLIANT
    assert report.summary.assets_included == 2
    assert report.summary.assets_excluded == 0


@pytest.mark.smoke
@pytest.mark.anyio
async def test_payearly_happy_path_route_status_case_insensitive() -> None:
    payload: list[dict[str, Any]] = [
        {
            "external_id": "P-1",
            "status": "PERFORMING",
            "is_eligible": True,
            "outstanding_principal_amount": "1000",
            "total_fee_amount": "10",
            "total_principal_amount": "1000",
            "created_at": "2026-01-01",
            "due_date": "2026-01-31",
        }
    ]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/facilities/payearly/covenant-report", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["facility"] == "payearly"
    assert data["included_assets"] == ["P-1"]
    assert data["summary"]["assets_included"] == 1


@pytest.mark.smoke
def test_payearly_normalizer_preserves_timestamp_time_of_day() -> None:
    normalized = normalize_payearly_assets(
        [
            {
                "external_id": "P-TS",
                "status": "performing",
                "is_eligible": True,
                "outstanding_principal_amount": "100",
                "total_fee_amount": "1",
                "total_principal_amount": "100",
                "created_at": "2026-01-01T23:15:30",
                "due_date": "2026-01-02T01:45:30",
            }
        ]
    )

    assert normalized[0].created_at == datetime(2026, 1, 1, 23, 15, 30)
    assert normalized[0].due_date == datetime(2026, 1, 2, 1, 45, 30)


@pytest.mark.smoke
def test_payearly_short_timestamp_tenor_is_not_truncated_to_calendar_days() -> None:
    report = generate_payearly_covenant_report(
        [
            {
                "external_id": "P-2H",
                "status": "performing",
                "is_eligible": True,
                "outstanding_principal_amount": "100",
                "total_fee_amount": "1",
                "total_principal_amount": "100",
                "created_at": "2026-01-01T23:00:00",
                "due_date": "2026-01-02T01:00:00",
            }
        ]
    )

    assert report.summary.assets_included == 1
    assert report.effective_rate_percentage == Decimal("4380.0")
    assert report.effective_rate_percentage > Decimal("365")


@pytest.mark.smoke
def test_payearly_date_only_inputs_still_work_using_midnight_datetimes() -> None:
    normalized = normalize_payearly_assets(
        [
            {
                "external_id": "P-DATE",
                "status": "performing",
                "is_eligible": True,
                "outstanding_principal_amount": "100",
                "total_fee_amount": "1",
                "total_principal_amount": "100",
                "created_at": "2026-01-01",
                "due_date": "2026-01-02",
            }
        ]
    )

    assert normalized[0].created_at == datetime(2026, 1, 1, 0, 0, 0)
    assert normalized[0].due_date == datetime(2026, 1, 2, 0, 0, 0)

    report = generate_payearly_covenant_report(
        [
            {
                "external_id": "P-DATE",
                "status": "performing",
                "is_eligible": True,
                "outstanding_principal_amount": "100",
                "total_fee_amount": "1",
                "total_principal_amount": "100",
                "created_at": "2026-01-01",
                "due_date": "2026-01-02",
            }
        ]
    )

    assert report.summary.assets_included == 1
    assert report.effective_rate_percentage == Decimal("365.00")


@pytest.mark.smoke
def test_nomina_happy_path_service() -> None:
    report = generate_nomina_covenant_report(
        [
            {
                "external_id": "N-1",
                "status": "active",
                "is_eligible": True,
                "outstanding_amount": "500",
                "fee_percentage": "2",
                "origination_date": "01/01/2026",
                "maturity_date": "01/07/2026",
            }
        ]
    )

    assert report.covenant_status == CovenantStatus.COMPLIANT
    assert report.summary.assets_included == 1


@pytest.mark.smoke
def test_nomina_end_of_month_rollover_counts_as_one_month() -> None:
    report = generate_nomina_covenant_report(
        [
            {
                "external_id": "N-EOM",
                "status": "active",
                "is_eligible": True,
                "outstanding_amount": "500",
                "fee_percentage": "2",
                "origination_date": "2026-01-31",
                "maturity_date": "2026-02-28",
            }
        ]
    )

    assert report.summary.assets_included == 1
    assert report.summary.assets_excluded == 0
    assert report.included_assets == ["N-EOM"]
    assert report.excluded_assets == []
    assert report.effective_rate_percentage == Decimal("24")


@pytest.mark.smoke
def test_nomina_end_of_month_rollover_leap_year_counts_as_one_month() -> None:
    report = generate_nomina_covenant_report(
        [
            {
                "external_id": "N-EOM-LEAP",
                "status": "active",
                "is_eligible": True,
                "outstanding_amount": "500",
                "fee_percentage": "2",
                "origination_date": "2024-01-31",
                "maturity_date": "2024-02-29",
            }
        ]
    )

    assert report.summary.assets_included == 1
    assert report.summary.assets_excluded == 0
    assert report.included_assets == ["N-EOM-LEAP"]
    assert report.excluded_assets == []
    assert report.effective_rate_percentage == Decimal("24")


@pytest.mark.smoke
def test_nomina_non_positive_date_range_is_still_excluded() -> None:
    report = generate_nomina_covenant_report(
        [
            {
                "external_id": "N-BAD-RANGE",
                "status": "active",
                "is_eligible": True,
                "outstanding_amount": "500",
                "fee_percentage": "2",
                "origination_date": "2026-02-28",
                "maturity_date": "2026-01-31",
            }
        ]
    )

    assert report.summary.assets_included == 0
    assert report.summary.assets_excluded == 1
    assert report.excluded_assets[0].external_id == "N-BAD-RANGE"
    assert "invalid origination_date or maturity_date" in report.excluded_assets[0].reasons


@pytest.mark.smoke
def test_educa_missing_interest_rate_is_excluded() -> None:
    report = generate_educa_covenant_report(
        [
            {
                "external_id": "E-NULL",
                "status": "Open",
                "is_eligible": True,
                "loan_status": "current",
                "interest_rate_percentage": None,
                "outstanding_amount": "100",
            }
        ]
    )

    assert report.summary.assets_excluded == 1
    assert report.excluded_assets[0].external_id == "E-NULL"
    assert "missing interest_rate_percentage" in report.excluded_assets[0].reasons


@pytest.mark.smoke
def test_educa_threshold_boundary_equal_is_breach() -> None:
    report = generate_educa_covenant_report(
        [
            {
                "external_id": "E-B",
                "status": "open",
                "is_eligible": True,
                "loan_status": "current",
                "interest_rate_percentage": "22.0",
                "outstanding_amount": "100",
            }
        ]
    )

    assert report.effective_rate_percentage == 22
    assert report.covenant_status == CovenantStatus.BREACH


@pytest.mark.smoke
def test_educa_zero_outstanding_is_included() -> None:
    report = generate_educa_covenant_report(
        [
            {
                "external_id": "E-ZERO",
                "status": "open",
                "is_eligible": True,
                "loan_status": "current",
                "interest_rate_percentage": "18.5",
                "outstanding_amount": "0",
            }
        ]
    )

    assert report.summary.assets_included == 1
    assert report.summary.assets_excluded == 0
    assert report.included_assets == ["E-ZERO"]
    assert report.excluded_assets == []
    assert report.effective_rate_percentage == 0
    assert report.covenant_status == CovenantStatus.COMPLIANT


@pytest.mark.smoke
def test_educa_negative_outstanding_is_excluded_with_explicit_reason() -> None:
    report = generate_educa_covenant_report(
        [
            {
                "external_id": "E-NEG",
                "status": "open",
                "is_eligible": True,
                "loan_status": "current",
                "interest_rate_percentage": "18.5",
                "outstanding_amount": "-1",
            }
        ]
    )

    assert report.summary.assets_included == 0
    assert report.summary.assets_excluded == 1
    assert report.included_assets == []
    assert report.excluded_assets[0].external_id == "E-NEG"
    assert "outstanding_amount must be >= 0" in report.excluded_assets[0].reasons


@pytest.mark.smoke
def test_educa_negative_outstanding_portfolio_does_not_become_compliant() -> None:
    report = generate_educa_covenant_report(
        [
            {
                "external_id": "E-NEG-ONLY",
                "status": "open",
                "is_eligible": True,
                "loan_status": "current",
                "interest_rate_percentage": "18.5",
                "outstanding_amount": "-100",
            }
        ]
    )

    assert report.summary.assets_included == 0
    assert report.summary.assets_excluded == 1
    assert report.effective_rate_percentage == 0
    assert report.covenant_status == CovenantStatus.BREACH


@pytest.mark.smoke
def test_educa_no_eligible_assets_defaults_to_breach_with_zero_rate() -> None:
    report = generate_educa_covenant_report(
        [
            {
                "external_id": "E-NOPE",
                "status": "closed",
                "is_eligible": False,
                "loan_status": "late",
                "interest_rate_percentage": None,
                "outstanding_amount": None,
            }
        ]
    )

    assert report.summary.assets_included == 0
    assert report.effective_rate_percentage == 0
    assert report.covenant_status == CovenantStatus.BREACH


@pytest.mark.smoke
def test_to_decimal_rejects_nan() -> None:
    assert to_decimal("NaN") is None


@pytest.mark.smoke
def test_to_decimal_rejects_infinity() -> None:
    assert to_decimal("Infinity") is None
    assert to_decimal("-Infinity") is None


@pytest.mark.smoke
@pytest.mark.anyio
async def test_educa_route_non_finite_decimal_does_not_crash() -> None:
    payload: list[dict[str, Any]] = [
        {
            "external_id": "E-INF",
            "status": "open",
            "is_eligible": True,
            "loan_status": "current",
            "interest_rate_percentage": "Infinity",
            "outstanding_amount": "100",
        }
    ]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/facilities/educa/covenant-report", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["assets_excluded"] == 1
    assert data["summary"]["assets_included"] == 0


@pytest.mark.smoke
def test_no_eligible_assets_defaults_to_breach_with_zero_rate() -> None:
    report = generate_payearly_covenant_report(
        [
            {
                "external_id": "P-X",
                "status": "defaulted",
                "is_eligible": False,
                "outstanding_principal_amount": "0",
                "total_fee_amount": "10",
                "total_principal_amount": "1000",
                "created_at": "2026-01-01",
                "due_date": "2026-01-31",
            }
        ]
    )

    assert report.summary.assets_included == 0
    assert report.effective_rate_percentage == 0
    assert report.covenant_status == CovenantStatus.BREACH


@pytest.mark.smoke
def test_payearly_effective_rate_is_reported_in_percentage_units() -> None:
    report = generate_payearly_covenant_report(
        [
            {
                "external_id": "P-100X",
                "status": "performing",
                "is_eligible": True,
                "outstanding_principal_amount": "1000",
                "total_fee_amount": "10",
                "total_principal_amount": "1000",
                "created_at": "2026-01-01",
                "due_date": "2026-01-21",
            }
        ]
    )

    assert report.effective_rate_percentage == Decimal("18.25")
    assert report.covenant_status == CovenantStatus.BREACH


@pytest.mark.smoke
def test_payearly_threshold_boundary_equal_is_breach() -> None:
    report = generate_payearly_covenant_report(
        [
            {
                "external_id": "P-B",
                "status": "performing",
                "is_eligible": True,
                "outstanding_principal_amount": "1000",
                "total_fee_amount": "30",
                "total_principal_amount": "1000",
                "created_at": "2026-01-01",
                "due_date": "2027-01-01",
            }
        ]
    )

    assert report.effective_rate_percentage == Decimal("3.00")
    assert report.covenant_status == CovenantStatus.BREACH
