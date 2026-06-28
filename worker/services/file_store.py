import json
from contextlib import contextmanager
from pathlib import Path

from filelock import FileLock, Timeout


class FileStore:
    def __init__(self, output_file: str) -> None:
        self._path = Path(output_file)
        self._lock_path = self._path.with_suffix(f"{self._path.suffix}.lock")
        self._lock = FileLock(str(self._lock_path))
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def try_lock(self):
        try:
            self._lock.acquire(timeout=0)
        except Timeout:
            yield False
            return

        try:
            yield True
        finally:
            self._lock.release()

    def read_last_entry(self) -> dict | None:
        if not self._path.exists() or self._path.stat().st_size == 0:
            return None

        last_line = self._read_last_non_empty_line()
        if last_line is None:
            return None

        return json.loads(last_line)

    def _read_last_non_empty_line(self) -> str | None:
        with self._path.open("rb") as file:
            file.seek(0, 2)
            position = file.tell() - 1

            while position >= 0:
                file.seek(position)
                current_byte = file.read(1)
                if current_byte not in (b"\n", b"\r"):
                    break
                position -= 1

            if position < 0:
                return None

            line_bytes = bytearray()

            while position >= 0:
                file.seek(position)
                current_byte = file.read(1)
                if current_byte == b"\n":
                    break
                line_bytes.extend(current_byte)
                position -= 1

        return bytes(reversed(line_bytes)).decode("utf-8")

    def append_entries(self, entries: list[dict]) -> int:
        if not entries:
            return 0

        with self._path.open("a", encoding="utf-8") as file:
            for entry in entries:
                file.write(json.dumps(entry, ensure_ascii=False))
                file.write("\n")

        return len(entries)
