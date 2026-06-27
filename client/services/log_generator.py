from http import HTTPMethod
from random import Random

from client.models.log_entry import GeneratedLogEntry

HTTP_METHODS = (
    HTTPMethod.GET.value,
    HTTPMethod.POST.value,
    HTTPMethod.PUT.value,
    HTTPMethod.PATCH.value,
    HTTPMethod.DELETE.value,
)
URIS = (
    "/api/users",
    "/api/orders",
    "/api/products",
    "/api/products/123",
    "/api/cart",
    "/api/payment",
)
STATUS_CODES = (200, 201, 204, 400, 401, 403, 404, 500)


class LogGenerator:
    def __init__(self, randomizer: Random | None = None) -> None:
        self._random = randomizer or Random()

    def generate(self) -> GeneratedLogEntry:
        return GeneratedLogEntry(
            ip=self._generate_ip(),
            method=self._random.choice(HTTP_METHODS),
            uri=self._random.choice(URIS),
            status_code=self._random.choice(STATUS_CODES),
        )

    def _generate_ip(self) -> str:
        network = self._random.choice(("10", "172", "192"))

        if network == "10":
            return (
                f"10.{self._random.randint(0, 255)}."
                f"{self._random.randint(0, 255)}.{self._random.randint(1, 254)}"
            )

        if network == "172":
            return (
                f"172.{self._random.randint(16, 31)}."
                f"{self._random.randint(0, 255)}.{self._random.randint(1, 254)}"
            )

        return f"192.168.{self._random.randint(0, 255)}.{self._random.randint(1, 254)}"
