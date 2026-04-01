from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.models import PublishedCovenantReportModel
from app.domain.models import CovenantReportPublication, PublishCovenantReportCommand


class SqlAlchemyCovenantReportPublisher:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def publish(self, command: PublishCovenantReportCommand) -> CovenantReportPublication:
        existing = await self._get_existing(command)
        if existing is not None:
            return _to_publication(existing, was_already_published=True)

        new_record = PublishedCovenantReportModel(
            facility=command.facility,
            calculation_version=command.calculation_version,
            normalized_payload_json=command.normalized_payload_json,
            normalized_payload_hash=command.normalized_payload_hash,
            effective_rate_percentage=command.effective_rate_percentage,
            threshold_percentage=command.threshold_percentage,
            covenant_status=command.covenant_status.value,
            total_assets_evaluated=command.total_assets_evaluated,
            assets_included_count=command.assets_included_count,
            assets_excluded_count=command.assets_excluded_count,
            included_assets=command.included_assets,
            excluded_assets=command.excluded_assets,
        )

        try:
            self._session.add(new_record)
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()
            existing_after_conflict = await self._get_existing(command)
            if existing_after_conflict is not None:
                return _to_publication(existing_after_conflict, was_already_published=True)
            raise
        except Exception:
            await self._session.rollback()
            raise

        try:
            await self._session.refresh(new_record)
            return _to_publication(new_record, was_already_published=False)
        except Exception:
            existing_after_refresh_failure = await self._get_existing(command)
            if existing_after_refresh_failure is not None:
                return _to_publication(existing_after_refresh_failure, was_already_published=False)
            raise

    async def _get_existing(self, command: PublishCovenantReportCommand) -> PublishedCovenantReportModel | None:
        statement: Select[tuple[PublishedCovenantReportModel]] = select(PublishedCovenantReportModel).where(
            PublishedCovenantReportModel.facility == command.facility,
            PublishedCovenantReportModel.calculation_version == command.calculation_version,
            PublishedCovenantReportModel.normalized_payload_hash == command.normalized_payload_hash,
        )
        result = await self._session.execute(statement)
        return result.scalar_one_or_none()


def _to_publication(
    record: PublishedCovenantReportModel,
    *,
    was_already_published: bool,
) -> CovenantReportPublication:
    return CovenantReportPublication(
        id=record.id,
        calculation_version=record.calculation_version,
        normalized_payload_hash=record.normalized_payload_hash,
        published_at=record.published_at,
        was_already_published=was_already_published,
    )
