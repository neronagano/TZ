import httpx


class ServerClient:
    def __init__(self, base_url: str, page_size: int) -> None:
        self._client = httpx.Client(base_url=base_url.rstrip("/"), timeout=5.0)
        self._page_size = page_size

    def __enter__(self) -> "ServerClient":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._client.close()

    def fetch_initial_entries(self) -> list[dict]:
        response = self._client.get(
            "/api/data",
            params={"limit": self._page_size, "offset": 0},
        )
        response.raise_for_status()
        payload = response.json()

        return payload["items"]

    def fetch_new_entries(
        self,
        cursor_created_at: str,
        cursor_id: str,
    ) -> list[dict]:
        response = self._client.get(
            "/api/data",
            params={
                "limit": self._page_size,
                "offset": 0,
                "cursor_created_at": cursor_created_at,
                "cursor_id": cursor_id,
            },
        )
        response.raise_for_status()
        payload = response.json()

        return payload["items"]
