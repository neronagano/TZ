import logging
import time
from concurrent.futures import ThreadPoolExecutor
from random import Random

from client.models.log_entry import DeliveryResult
from client.services.api_client import WebAPIClient
from client.services.log_generator import LogGenerator
from core.settings import Settings

logger = logging.getLogger(__name__)


class ClientService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def run(self) -> None:
        logger.info(
            "client service started",
            extra={
                "workers": self._settings.CLIENT_WORKERS,
                "requests_per_worker": self._settings.CLIENT_REQUESTS_PER_WORKER,
                "api_url": self._settings.API_URL,
            },
        )

        with ThreadPoolExecutor(
            max_workers=self._settings.CLIENT_WORKERS,
            thread_name_prefix="client-worker",
        ) as executor:
            futures = [
                executor.submit(self._run_worker, worker_id)
                for worker_id in range(1, self._settings.CLIENT_WORKERS + 1)
            ]

            for future in futures:
                future.result()

        logger.info("client service completed")

    def _run_worker(self, worker_id: int) -> None:
        randomizer = Random()
        generator = LogGenerator(randomizer=randomizer)
        with WebAPIClient(
            base_url=self._settings.API_URL,
            timeout_seconds=self._settings.CLIENT_REQUEST_TIMEOUT_SECONDS,
            max_attempts=self._settings.CLIENT_MAX_ATTEMPTS,
            retry_backoff_ms=self._settings.CLIENT_RETRY_BACKOFF_MS,
        ) as api_client:
            for request_index in range(self._settings.CLIENT_REQUESTS_PER_WORKER):
                log_entry = generator.generate()
                result = api_client.send_log(log_entry)
                self._log_delivery(worker_id, log_entry.as_line(), result)

                if request_index < self._settings.CLIENT_REQUESTS_PER_WORKER - 1:
                    delay_ms = randomizer.randint(0, self._settings.CLIENT_MAX_DELAY_MS)
                    time.sleep(delay_ms / 1000)

    def _log_delivery(
        self,
        worker_id: int,
        log_line: str,
        result: DeliveryResult,
    ) -> None:
        if result.success:
            logger.info(
                "log delivered",
                extra={
                    "worker_id": worker_id,
                    "log": log_line,
                    "response_status": result.status_code,
                    "attempts": result.attempts,
                },
            )
            return

        logger.warning(
            "log delivery failed",
            extra={
                "worker_id": worker_id,
                "log": log_line,
                "response_status": result.status_code,
                "attempts": result.attempts,
                "error": result.error,
            },
        )
