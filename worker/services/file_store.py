import json
from contextlib import contextmanager
from pathlib import Path

try:
    import fcntl
except ModuleNotFoundError:  # pragma: no cover - Windows fallback for local development
    fcntl = None


class FileStore:
    def __init__(self, output_file: str) -> None:
        self._path = Path(output_file)
        self._lock_path = self._path.with_suffix(f"{self._path.suffix}.lock")
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def try_lock(self):
        if fcntl is None:
            raise RuntimeError("File locking requires Unix environment")

        with self._lock_path.open("a+", encoding="utf-8") as lock_file:
            try:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                yield False
                return

            try:
                yield True
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

    def read_last_entry(self) -> dict | None:
        if not self._path.exists():
            return None

        last_line: str | None = None

        with self._path.open("r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    last_line = line

        if last_line is None:
            return None

        return json.loads(last_line)

    def append_entries(self, entries: list[dict]) -> int:
        if not entries:
            return 0

        with self._path.open("a", encoding="utf-8") as file:
            for entry in entries:
                file.write(json.dumps(entry, ensure_ascii=False))
                file.write("\n")

        return len(entries)
