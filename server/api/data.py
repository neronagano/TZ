import ipaddress
from http import HTTPMethod
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/data", tags=["Data"])

def _validate_ip_address(ip_addres: str):
    try:
        ipaddress.ip_address(ip_addres)
        return True

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="IP address value error"
        )

def _validate_method(method):
    try:
        HTTPMethod(method.upper())
        return True

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Method value error"
        )

def _validate_endpoint(endpoint: str) -> None:
    parsed = urlparse(endpoint)
    if not endpoint.startswith("/") or parsed.scheme or parsed.netloc:
        raise HTTPException(
            status_code=400,
            detail="Endpoint value error",
        )

@router.get("/")
async def main(log: str):
    ip_address, method, endpoint, status_code = log.split()
    _validate_ip_address(ip_address)
    _validate_method(method)
    _validate_endpoint(endpoint)
    return "succes"
