from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.application.use_cases.generate_payearly_covenant_report import (
    generate_and_publish_payearly_covenant_report,
)
from app.core.db.hashing import hash_normalized_payload, normalized_assets_to_json
from app.core.db.models import PublishedCovenantReportModel
from app.core.db.repositories import SqlAlchemyCovenantReportPublisher
from app.core.normalizers import normalize_educa_assets
from app.domain.models import (
    CovenantReportPublication,
    CovenantStatus,
    PublishCovenantReportCommand,
)


@pytest.mark.smoke
def test_normalized_payload_hash_is_deterministic_when_asset_order_changes() -> None:
    payload_a = [
        {
            "external_id": "E-2",
            "status": "open",
            "is_eligible": True,
            "loan_status": "current",
            "interest_rate_percentage": "20.0",
            "outstanding_amount": "100",
        },
        {
            "external_id": "E-1",
            "status": "open",
            "is_eligible": True,
            "loan_status": "current",
            "interest_rate_percentage": "19.0",
            "outstanding_amount": "200",
        },
    ]
    payload_b = list(reversed(payload_a))

    normalized_a = normalize_educa_assets(payload_a)
    normalized_b = normalize_educa_assets(payload_b)

    hash_a = hash_normalized_payload(normalized_assets_to_json(normalized_a))
    hash_b = hash_normalized_payload(normalized_assets_to_json(normalized_b))

    assert hash_a == hash_b


@pytest.mark.smoke
def test_normalized_payload_hash_is_stable_for_decimal_scale_variants() -> None:
    payload_a = [
        {
            "external_id": "E-1",
            "interest_rate_percentage": Decimal("21.5"),
            "outstanding_amount": Decimal("0.00"),
        }
    ]
    payload_b = [
        {
            "external_id": "E-1",
            "interest_rate_percentage": Decimal("21.50"),
            "outstanding_amount": Decimal("0"),
        }
    ]

    hash_a = hash_normalized_payload(payload_a)
    hash_b = hash_normalized_payload(payload_b)

    assert hash_a == hash_b


class _FakePublisher:
    async def publish(self, command: PublishCovenantReportCommand) -> CovenantReportPublication:
        return CovenantReportPublication(
            id=99,
            calculation_version=command.calculation_version,
            normalized_payload_hash=command.normalized_payload_hash,
            published_at=datetime(2026, 1, 1, tzinfo=UTC),
            was_already_published=False,
        )


def _build_publish_command() -> PublishCovenantReportCommand:
    return PublishCovenantReportCommand(
        facility="educa",
        calculation_version="v1",
        normalized_payload_json=[{"external_id": "E-1", "interest_rate_percentage": "21.5"}],
        normalized_payload_hash="a" * 64,
        effective_rate_percentage=Decimal("21.5"),
        threshold_percentage=Decimal("22.0"),
        covenant_status=CovenantStatus.COMPLIANT,
        total_assets_evaluated=1,
        assets_included_count=1,
        assets_excluded_count=0,
        included_assets=["E-1"],
        excluded_assets=[],
    )


@pytest.mark.smoke
@pytest.mark.anyio
async def test_publisher_recovers_if_refresh_fails_after_successful_commit() -> None:
    class _FakeSession:
        def add(self, _record: PublishedCovenantReportModel) -> None:
            return None

        async def commit(self) -> None:
            return None

        async def refresh(self, _record: PublishedCovenantReportModel) -> None:
            raise RuntimeError("refresh failed")

        async def rollback(self) -> None:
            return None

    recovered_record = PublishedCovenantReportModel(
        id=123,
        facility="educa",
        calculation_version="v1",
        normalized_payload_json=[{"external_id": "E-1"}],
        normalized_payload_hash="a" * 64,
        effective_rate_percentage=Decimal("21.5"),
        threshold_percentage=Decimal("22.0"),
        covenant_status=CovenantStatus.COMPLIANT.value,
        total_assets_evaluated=1,
        assets_included_count=1,
        assets_excluded_count=0,
        included_assets=["E-1"],
        excluded_assets=[],
        published_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    publisher = SqlAlchemyCovenantReportPublisher(_FakeSession())  # type: ignore[arg-type]
    publisher._get_existing = AsyncMock(side_effect=[None, recovered_record])  # type: ignore[method-assign]

    publication = await publisher.publish(_build_publish_command())

    assert publication.id == 123
    assert publication.was_already_published is False


@pytest.mark.smoke
@pytest.mark.anyio
async def test_use_case_attaches_publication_metadata() -> None:
    report = await generate_and_publish_payearly_covenant_report(
        [
            {
                "external_id": "P-1",
                "status": "performing",
                "is_eligible": True,
                "outstanding_principal_amount": "1000",
                "total_fee_amount": "10",
                "total_principal_amount": "1000",
                "created_at": "2026-01-01",
                "due_date": "2026-01-31",
            }
        ],
        publisher=_FakePublisher(),
    )

    assert report.publication is not None
    assert report.publication.id == 99
    assert report.publication.calculation_version == "v1"
    assert len(report.publication.normalized_payload_hash) == 64
    assert report.effective_rate_percentage > 0
