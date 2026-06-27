import time

import httpx

from client.models.log_entry import DeliveryResult, GeneratedLogEntry


class WebAPIClient:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: float,
        max_attempts: int,
        retry_backoff_ms: int,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=timeout_seconds,
        )
        self._max_attempts = max_attempts
        self._retry_backoff_ms = retry_backoff_ms

    def __enter__(self) -> "WebAPIClient":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._client.close()

    def send_log(self, log_entry: GeneratedLogEntry) -> DeliveryResult:
        payload = {"log": log_entry.as_line()}
        last_error: str | None = None

        for attempt in range(1, self._max_attempts + 1):
            try:
                response = self._client.post("/api/data", json=payload)
            except httpx.HTTPError as exc:
                last_error = str(exc)
                if attempt < self._max_attempts:
                    self._sleep_before_retry(attempt)
                    continue

                return DeliveryResult(attempts=attempt, error=last_error)

            if response.status_code >= 500 and attempt < self._max_attempts:
                last_error = response.text
                self._sleep_before_retry(attempt)
                continue

            if response.status_code == 201:
                return DeliveryResult(
                    attempts=attempt,
                    status_code=response.status_code,
                )

            return DeliveryResult(
                attempts=attempt,
                status_code=response.status_code,
                error=response.text or response.reason_phrase,
            )

        return DeliveryResult(
            attempts=self._max_attempts,
            error=last_error or "Unknown error",
        )

    def _sleep_before_retry(self, attempt: int) -> None:
        if self._retry_backoff_ms <= 0:
            return

        time.sleep((self._retry_backoff_ms * attempt) / 1000)
