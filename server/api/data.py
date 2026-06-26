import ipaddress
from http import HTTPMethod
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/data", tags=["Data"])

ALLOWED_METHODS = {
    HTTPMethod.GET.value,
    HTTPMethod.POST.value,
    HTTPMethod.PUT.value,
    HTTPMethod.PATCH.value,
    HTTPMethod.DELETE.value,
}


def _validate_ip_address(ip_address: str) -> str:
    try:
        ipaddress.ip_address(ip_address)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="IP address value error",
        )

    return ip_address


def _validate_method(method: str) -> str:
    normalized_method = method.upper()
    if normalized_method not in ALLOWED_METHODS:
        raise HTTPException(
            status_code=400,
            detail="Method value error",
        )

    return normalized_method


def _validate_endpoint(endpoint: str) -> str:
    parsed = urlparse(endpoint)
    if not endpoint.startswith("/") or parsed.scheme or parsed.netloc:
        raise HTTPException(
            status_code=400,
            detail="Endpoint value error",
        )

    return endpoint


def _validate_status_code(status_code: str) -> int:
    try:
        value = int(status_code)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Status code value error",
        )

    if not 100 <= value <= 599:
        raise HTTPException(
            status_code=400,
            detail="Status code out of range",
        )

    return value


def parse_log(log: str) -> dict[str, str | int]:
    if not log or not log.strip():
        raise HTTPException(
            status_code=400,
            detail="Log line is empty",
        )

    parts = log.split()
    if len(parts) != 4:
        raise HTTPException(
            status_code=400,
            detail="Log line must contain exactly 4 parts",
        )

    ip_address, method, endpoint, status_code = parts
    ip_address = _validate_ip_address(ip_address)
    method = _validate_method(method)
    endpoint = _validate_endpoint(endpoint)
    status_code = _validate_status_code(status_code)

    return {
        "ip": ip_address,
        "method": method,
        "uri": endpoint,
        "status_code": status_code,
    }


@router.get("/")
async def data_endpoint(log: str):
    parsed_log = parse_log(log)
    return {"log": parsed_log}
