from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from app.api.schemas.common import SchemaModel
from app.api.schemas.publication import PublicationSchema
from app.domain.models import CovenantReport, CovenantStatus, ExcludedAsset


class ExcludedAssetSchema(SchemaModel):
    external_id: str
    reasons: list[str]

    @classmethod
    def from_domain(cls, excluded_asset: ExcludedAsset) -> ExcludedAssetSchema:
        return cls(external_id=excluded_asset.external_id, reasons=excluded_asset.reasons)


class CovenantReportSummarySchema(SchemaModel):
    total_assets_evaluated: int
    assets_included: int
    assets_excluded: int


class CovenantReportResponseSchema(SchemaModel):
    facility: str
    effective_rate_percentage: str
    covenant_status: CovenantStatus
    summary: CovenantReportSummarySchema
    included_assets: list[str]
    excluded_assets: list[ExcludedAssetSchema]
    publication: PublicationSchema

    @classmethod
    def from_domain(cls, report: CovenantReport) -> CovenantReportResponseSchema:
        if report.publication is None:
            msg = "publication metadata is required to build API response"
            raise ValueError(msg)
        formatted_rate = report.effective_rate_percentage.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return cls(
            facility=report.facility,
            effective_rate_percentage=f"{formatted_rate:.2f}",
            covenant_status=report.covenant_status,
            summary=CovenantReportSummarySchema(
                total_assets_evaluated=report.summary.total_assets_evaluated,
                assets_included=report.summary.assets_included,
                assets_excluded=report.summary.assets_excluded,
            ),
            included_assets=report.included_assets,
            excluded_assets=[ExcludedAssetSchema.from_domain(item) for item in report.excluded_assets],
            publication=PublicationSchema.from_domain(report.publication),
        )
