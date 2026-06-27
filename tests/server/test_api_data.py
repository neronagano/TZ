from datetime import UTC, datetime
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from server.database.engine import get_session
from server.main import app
from server.services.log_parser import get_parsed_log


@pytest.mark.asyncio
async def test_post_data_without_trailing_slash_returns_created(monkeypatch: pytest.MonkeyPatch) -> None:
    parsed_log = {
        "ip": "10.0.0.1",
        "method": "GET",
        "uri": "/api/ping",
        "status_code": 200,
    }

    class SavedLogEntry:
        id = uuid4()
        created_at = datetime(2026, 6, 26, 12, 0, tzinfo=UTC)
        status_code = 200

    async def fake_create_log_entry(_session: object, _parsed_log: dict[str, str | int]) -> SavedLogEntry:
        return SavedLogEntry()

    async def fake_get_session():
        yield object()

    monkeypatch.setattr("server.api.data.create_log_entry_service", fake_create_log_entry)
    app.dependency_overrides[get_parsed_log] = lambda: parsed_log
    app.dependency_overrides[get_session] = fake_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/data", json={"log": "ignored by override"})

    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json() == {
        "id": str(SavedLogEntry.id),
        "created_at": "2026-06-26T12:00:00Z",
        "log": parsed_log,
    }


@pytest.mark.asyncio
async def test_get_data_rejects_offset_with_cursor() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/data",
            params={
                "limit": 10,
                "offset": 1,
                "cursor_created_at": "2026-06-26T12:00:00Z",
                "cursor_id": "00000000-0000-0000-0000-000000000001",
            },
        )

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Value error, Offset must be 0 when cursor is used"
