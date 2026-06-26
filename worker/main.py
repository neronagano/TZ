import logging

from core.logging import configure_logging
from core.settings import settings
from worker.services.worker import WorkerService


def main() -> None:
    configure_logging()
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    worker = WorkerService(
        api_url=settings.WORKER_API_URL,
        poll_interval_seconds=settings.WORKER_POLL_INTERVAL_SECONDS,
        page_size=settings.WORKER_PAGE_SIZE,
        output_file=settings.WORKER_OUTPUT_FILE,
    )
    worker.run()


if __name__ == "__main__":
    main()
