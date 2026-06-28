from worker.services.file_store import FileStore


def test_read_last_entry_returns_last_jsonl_record(tmp_path) -> None:
    store = FileStore(str(tmp_path / "log_entries.jsonl"))
    store.append_entries(
        [
            {"id": "1", "created_at": "2026-06-28T10:00:00Z"},
            {"id": "2", "created_at": "2026-06-28T10:00:01Z"},
        ]
    )

    result = store.read_last_entry()

    assert result == {"id": "2", "created_at": "2026-06-28T10:00:01Z"}


def test_read_last_entry_returns_none_for_empty_file(tmp_path) -> None:
    store = FileStore(str(tmp_path / "log_entries.jsonl"))

    assert store.read_last_entry() is None
