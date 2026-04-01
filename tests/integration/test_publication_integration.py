from __future__ import annotations

import os
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.db.base import Base
from app.core.db.models import PublishedCovenantReportModel
from app.core.db.repositories import SqlAlchemyCovenantReportPublisher
from app.domain.models import CovenantStatus, PublishCovenantReportCommand
from app.main import app

pytestmark = pytest.mark.integration


def _require_test_database_url() -> str:
    test_database_url = os.getenv("TEST_DATABASE_URL")
    if not test_database_url:
        pytest.skip("TEST_DATABASE_URL is required for integration tests")

    lowered = test_database_url.lower()
    if "localhost" not in lowered and "127.0.0.1" not in lowered:
        pytest.skip("Integration tests only run against local database URLs")
    if "test" not in lowered:
        pytest.skip("Integration tests require a test database URL")

    return test_database_url


@pytest.fixture
async def session_maker() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    database_url = _require_test_database_url()
    engine = create_async_engine(database_url, pool_pre_ping=True)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    maker = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    try:
        yield maker
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.fixture(autouse=True)
async def reset_reports(session_maker: async_sessionmaker[AsyncSession]) -> None:
    async with session_maker() as session:
        await session.execute(delete(PublishedCovenantReportModel))
        await session.commit()


def _build_command(*, calculation_version: str = "v1") -> PublishCovenantReportCommand:
    return PublishCovenantReportCommand(
        facility="educa",
        calculation_version=calculation_version,
        normalized_payload_json=[
            {
                "external_id": "E-1",
                "status": "open",
                "is_eligible": True,
                "loan_status": "current",
                "interest_rate_percentage": "21.5",
                "outstanding_amount": "1000",
            }
        ],
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


@pytest.mark.anyio
async def test_publication_creates_record_when_none_exists(
    session_maker: async_sessionmaker[AsyncSession],
) -> None:
    async with session_maker() as session:
        publisher = SqlAlchemyCovenantReportPublisher(session)
        publication = await publisher.publish(_build_command())

        count = await session.scalar(select(func.count()).select_from(PublishedCovenantReportModel))

    assert publication.was_already_published is False
    assert publication.id > 0
    assert count == 1


@pytest.mark.anyio
async def test_publication_is_idempotent_for_same_key(
    session_maker: async_sessionmaker[AsyncSession],
) -> None:
    async with session_maker() as session:
        publisher = SqlAlchemyCovenantReportPublisher(session)
        first = await publisher.publish(_build_command())
        second = await publisher.publish(_build_command())
        count = await session.scalar(select(func.count()).select_from(PublishedCovenantReportModel))

    assert first.id == second.id
    assert first.was_already_published is False
    assert second.was_already_published is True
    assert count == 1


@pytest.mark.anyio
async def test_publication_creates_new_record_when_version_changes(
    session_maker: async_sessionmaker[AsyncSession],
) -> None:
    async with session_maker() as session:
        publisher = SqlAlchemyCovenantReportPublisher(session)
        first = await publisher.publish(_build_command(calculation_version="v1"))
        second = await publisher.publish(_build_command(calculation_version="v2"))
        count = await session.scalar(select(func.count()).select_from(PublishedCovenantReportModel))

    assert second.id != first.id
    assert count == 2


@pytest.mark.anyio
async def test_api_response_includes_publication_metadata(
    monkeypatch: pytest.MonkeyPatch,
    session_maker: async_sessionmaker[AsyncSession],
) -> None:
    from app.api.routes import educa as educa_route

    class _SessionLocalOverride:
        def __call__(self) -> AsyncSession:
            return session_maker()

    monkeypatch.setattr(educa_route, "SessionLocal", _SessionLocalOverride())

    payload = [
        {
            "external_id": "E-1",
            "status": "open",
            "is_eligible": True,
            "loan_status": "current",
            "interest_rate_percentage": "21.5",
            "outstanding_amount": "1000",
        }
    ]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/facilities/educa/covenant-report", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert "publication" in body
    assert body["publication"]["calculation_version"] == "v1"
    assert len(body["publication"]["normalized_payload_hash"]) == 64
    assert body["publication"]["was_already_published"] is False
    assert datetime.fromisoformat(body["publication"]["published_at"].replace("Z", "+00:00")).tzinfo in {UTC}
