import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.smoke
@pytest.mark.anyio
async def test_health_ok() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.smoke
def test_fastapi_routes_wired() -> None:
    paths = {path for route in app.routes for path in [getattr(route, "path", None)] if isinstance(path, str)}

    assert app.title == "fence-api"
    assert "/health" in paths
    assert "/facilities/educa/covenant-report" in paths
    assert "/facilities/payearly/covenant-report" in paths
    assert "/facilities/nomina/covenant-report" in paths
