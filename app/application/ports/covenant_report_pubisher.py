from __future__ import annotations

from typing import Protocol

from app.domain.models import CovenantReportPublication, PublishCovenantReportCommand


class CovenantReportPublisher(Protocol):
    async def publish(self, command: PublishCovenantReportCommand) -> CovenantReportPublication: ...
