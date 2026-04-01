from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Body, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.api.schemas.covenant_report import CovenantReportResponseSchema
from app.application.use_cases import generate_and_publish_educa_covenant_report
from app.core.db.repositories import SqlAlchemyCovenantReportPublisher
from app.core.db.session import SessionLocal

router = APIRouter(prefix="/facilities/educa", tags=["facilities"])
RawEducaAssets = Annotated[list[dict[str, Any]], Body(...)]


@router.post("/covenant-report", response_model=CovenantReportResponseSchema)
async def educa_covenant_report(raw_assets: RawEducaAssets) -> CovenantReportResponseSchema:
    try:
        async with SessionLocal() as session:
            publisher = SqlAlchemyCovenantReportPublisher(session)
            report = await generate_and_publish_educa_covenant_report(raw_assets, publisher)
            return CovenantReportResponseSchema.from_domain(report)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Failed to publish covenant report") from exc
