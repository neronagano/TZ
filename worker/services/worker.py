import logging
import time

import httpx

from worker.services.file_store import FileStore
from worker.services.server_client import ServerClient

logger = logging.getLogger(__name__)


class WorkerService:
    def __init__(
        self,
        api_url: str,
        poll_interval_seconds: int,
        page_size: int,
        output_file: str,
    ) -> None:
        self._poll_interval_seconds = poll_interval_seconds
        self._file_store = FileStore(output_file)
        self._server_client = ServerClient(api_url, page_size)

    def run(self) -> None:
        logger.info("worker service started")

        with self._server_client:
            while True:
                self._run_cycle()
                time.sleep(self._poll_interval_seconds)

    def _run_cycle(self) -> None:
        with self._file_store.try_lock() as lock_acquired:
            if not lock_acquired:
                logger.info("worker skipped cycle because file is locked")
                return

            try:
                last_entry = self._file_store.read_last_entry()
                if last_entry is None:
                    self._save_initial_entries()
                    return

                self._save_new_entries(last_entry)
            except (httpx.HTTPError, KeyError, ValueError):
                logger.exception("worker sync failed")

    def _save_initial_entries(self) -> None:
        items = self._server_client.fetch_initial_entries()
        saved_count = self._file_store.append_entries(list(reversed(items)))

        logger.info("worker saved initial entries", extra={"saved_count": saved_count})

    def _save_new_entries(self, last_entry: dict) -> None:
        cursor_created_at = str(last_entry["created_at"])
        cursor_id = str(last_entry["id"])
        total_saved = 0

        while True:
            items = self._server_client.fetch_new_entries(
                cursor_created_at=cursor_created_at,
                cursor_id=cursor_id,
            )

            if not items:
                break

            total_saved += self._file_store.append_entries(items)
            last_item = items[-1]
            cursor_created_at = str(last_item["created_at"])
            cursor_id = str(last_item["id"])

        logger.info("worker saved new entries", extra={"saved_count": total_saved})
