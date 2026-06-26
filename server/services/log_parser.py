import ipaddress
import logging
from http import HTTPMethod
from urllib.parse import urlparse

from fastapi import HTTPException

from models.log_entry import LogCreateRequest

ALLOWED_METHODS = {
    HTTPMethod.GET.value,
    HTTPMethod.POST.value,
    HTTPMethod.PUT.value,
    HTTPMethod.PATCH.value,
    HTTPMethod.DELETE.value,
}

logger = logging.getLogger(__name__)

class LogParser:
    def parse(self, log: str) -> dict[str, str | int]:
        if not log or not log.strip():
            logger.warning("empty log line received")
            raise HTTPException(
                status_code=400,
                detail="Log line is empty",
            )

        parts = log.split()
        if len(parts) != 4:
            logger.warning("invalid log line parts count", extra={"parts_count": len(parts)})
            raise HTTPException(
                status_code=400,
                detail="Log line must contain exactly 4 parts",
            )

        ip_address, method, uri, status_code = parts
        ip_address = self._validate_ip_address(ip_address)
        self._validate_ip_v4(ip_address)
        method = self._validate_method(method)
        uri = self._validate_uri(uri)
        status_code = self._validate_status_code(status_code)

        parsed_log = {
            "ip": ip_address,
            "method": method,
            "uri": uri,
            "status_code": status_code,
        }

        logger.debug("log line parsed", extra=parsed_log)

        return parsed_log

    def _validate_ip_address(self, ip_address: str) -> str:
        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            logger.warning("invalid ip address", extra={"ip": ip_address})
            raise HTTPException(
                status_code=400,
                detail="IP address value error",
            )

        return ip_address

    def _validate_ip_v4(self, ip_address: str) -> None:
        if not isinstance(ipaddress.ip_address(ip_address), ipaddress.IPv4Address):
            raise HTTPException(
                status_code=400,
                detail="Only IPv4 is supported",
            )

    def _validate_method(self, method: str) -> str:
        normalized_method = method.upper()
        if normalized_method not in ALLOWED_METHODS:
            logger.warning("invalid http method", extra={"method": method})
            raise HTTPException(
                status_code=400,
                detail="Method value error",
            )

        return normalized_method

    def _validate_uri(self, uri: str) -> str:
        parsed = urlparse(uri)
        if not uri.startswith("/") or parsed.scheme or parsed.netloc:
            logger.warning("invalid uri", extra={"uri": uri})
            raise HTTPException(
                status_code=400,
                detail="URI value error",
            )

        return uri

    def _validate_status_code(self, status_code: str) -> int:
        try:
            value = int(status_code)
        except ValueError:
            logger.warning("status code is not numeric", extra={"status_code": status_code})
            raise HTTPException(
                status_code=400,
                detail="Status code value error",
            )

        if not 100 <= value <= 599:
            logger.warning("status code out of range", extra={"status_code": value})
            raise HTTPException(
                status_code=400,
                detail="Status code out of range",
            )

        return value


def get_parsed_log(payload: LogCreateRequest) -> dict[str, str | int]:
    return LogParser().parse(payload.log)
