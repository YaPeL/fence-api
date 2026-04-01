from __future__ import annotations

from datetime import datetime

from app.api.schemas.common import SchemaModel
from app.domain.models import CovenantReportPublication


class PublicationSchema(SchemaModel):
    id: int
    calculation_version: str
    normalized_payload_hash: str
    published_at: datetime
    was_already_published: bool

    @classmethod
    def from_domain(cls, publication: CovenantReportPublication) -> PublicationSchema:
        return cls(
            id=publication.id,
            calculation_version=publication.calculation_version,
            normalized_payload_hash=publication.normalized_payload_hash,
            published_at=publication.published_at,
            was_already_published=publication.was_already_published,
        )
