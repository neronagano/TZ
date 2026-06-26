from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class GeneratedLogEntry:
    ip: str
    method: str
    uri: str
    status_code: int

    def as_line(self) -> str:
        return f"{self.ip} {self.method} {self.uri} {self.status_code}"


@dataclass(slots=True, frozen=True)
class DeliveryResult:
    attempts: int
    status_code: int | None = None
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.status_code == 201 and self.error is None
