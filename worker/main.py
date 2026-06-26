import logging
import os

from core.logging import configure_logging
from worker.services.worker import WorkerService


def main() -> None:
    configure_logging()
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    worker = WorkerService(
        api_url=os.getenv("WORKER_API_URL", "http://localhost:8000"),
        poll_interval_seconds=int(os.getenv("WORKER_POLL_INTERVAL_SECONDS", "5")),
        page_size=int(os.getenv("WORKER_PAGE_SIZE", "100")),
        output_file=os.getenv("WORKER_OUTPUT_FILE", "worker/data/log_entries.jsonl"),
    )
    worker.run()


if __name__ == "__main__":
    main()
