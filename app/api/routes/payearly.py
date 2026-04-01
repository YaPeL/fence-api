from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Body

from app.api.schemas.covenant_report import CovenantReportResponseSchema
from app.application.use_cases import generate_payearly_covenant_report

router = APIRouter(prefix="/facilities/payearly", tags=["facilities"])
RawPayEarlyAssets = Annotated[list[dict[str, Any]], Body(...)]


@router.post("/covenant-report", response_model=CovenantReportResponseSchema)
async def payearly_covenant_report(raw_assets: RawPayEarlyAssets) -> CovenantReportResponseSchema:
    report = generate_payearly_covenant_report(raw_assets)
    return CovenantReportResponseSchema.from_domain(report)
