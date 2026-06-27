import pytest
from httpx import ASGITransport, AsyncClient

from server.database.engine import get_session
from server.main import app


@pytest.mark.asyncio
async def test_get_stats_returns_aggregated_counts(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_get_log_entry_stats(_session: object) -> tuple[dict[str, int], dict[str, int]]:
        return {"GET": 120, "POST": 95, "PUT": 12}, {"200": 210, "404": 15, "500": 2}

    async def fake_get_session():
        yield object()

    monkeypatch.setattr("server.api.stats.get_log_entry_stats_service", fake_get_log_entry_stats)
    app.dependency_overrides[get_session] = fake_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/stats")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "methods": {
            "GET": 120,
            "POST": 95,
            "PUT": 12,
        },
        "status_codes": {
            "200": 210,
            "404": 15,
            "500": 2,
        },
    }


@pytest.mark.asyncio
async def test_get_stats_returns_empty_mappings() -> None:
    async def fake_get_log_entry_stats(_session: object) -> tuple[dict[str, int], dict[str, int]]:
        return {}, {}

    async def fake_get_session():
        yield object()

    app.dependency_overrides[get_session] = fake_get_session

    from server.api import stats as stats_api

    original_service = stats_api.get_log_entry_stats_service
    stats_api.get_log_entry_stats_service = fake_get_log_entry_stats

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/stats")

    stats_api.get_log_entry_stats_service = original_service
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "methods": {},
        "status_codes": {},
    }
