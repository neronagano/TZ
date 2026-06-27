from worker.services.worker import WorkerService

import pytest


class FakeLock:
    def __init__(self, is_locked: bool) -> None:
        self._is_locked = is_locked

    def __enter__(self) -> bool:
        return self._is_locked

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class FakeFileStore:
    def __init__(self, last_entry: dict | None = None) -> None:
        self.last_entry = last_entry
        self.saved_batches: list[list[dict]] = []

    def try_lock(self) -> FakeLock:
        return FakeLock(True)

    def read_last_entry(self) -> dict | None:
        return self.last_entry

    def append_entries(self, entries: list[dict]) -> int:
        self.saved_batches.append(entries.copy())
        if entries:
            self.last_entry = entries[-1]
        return len(entries)


class FakeServerClient:
    def __init__(self, initial_entries: list[dict], pages: list[list[dict]]) -> None:
        self.initial_entries = initial_entries
        self.pages = pages
        self.cursor_calls: list[tuple[str, str]] = []

    def fetch_initial_entries(self) -> list[dict]:
        return self.initial_entries

    def fetch_new_entries(self, cursor_created_at: str, cursor_id: str) -> list[dict]:
        self.cursor_calls.append((cursor_created_at, cursor_id))
        if not self.pages:
            return []
        return self.pages.pop(0)

    def close(self) -> None:
        return None


@pytest.mark.asyncio
async def test_run_cycle_saves_initial_entries_in_oldest_first_order() -> None:
    service = WorkerService(
        api_url="http://server:8000",
        poll_interval_seconds=5,
        page_size=100,
        output_file="worker/data/test.jsonl",
    )
    service._file_store = FakeFileStore(last_entry=None)
    service._server_client = FakeServerClient(
        initial_entries=[
            {"id": "3", "created_at": "2026-06-26T12:00:03Z"},
            {"id": "2", "created_at": "2026-06-26T12:00:02Z"},
        ],
        pages=[],
    )

    service._run_cycle()

    assert service._file_store.saved_batches == [
        [
            {"id": "2", "created_at": "2026-06-26T12:00:02Z"},
            {"id": "3", "created_at": "2026-06-26T12:00:03Z"},
        ]
    ]


@pytest.mark.asyncio
async def test_run_cycle_uses_cursor_to_save_only_new_entries() -> None:
    service = WorkerService(
        api_url="http://server:8000",
        poll_interval_seconds=5,
        page_size=100,
        output_file="worker/data/test.jsonl",
    )
    service._file_store = FakeFileStore(
        last_entry={"id": "2", "created_at": "2026-06-26T12:00:02Z"}
    )
    service._server_client = FakeServerClient(
        initial_entries=[],
        pages=[
            [
                {"id": "3", "created_at": "2026-06-26T12:00:03Z"},
                {"id": "4", "created_at": "2026-06-26T12:00:04Z"},
            ],
            [],
        ],
    )

    service._run_cycle()

    assert service._server_client.cursor_calls == [
        ("2026-06-26T12:00:02Z", "2"),
        ("2026-06-26T12:00:04Z", "4"),
    ]
    assert service._file_store.saved_batches == [
        [
            {"id": "3", "created_at": "2026-06-26T12:00:03Z"},
            {"id": "4", "created_at": "2026-06-26T12:00:04Z"},
        ]
    ]
