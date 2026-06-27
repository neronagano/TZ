import pytest
from fastapi import HTTPException

from server.services.log_parser import LogParser


@pytest.mark.asyncio
async def test_parse_returns_normalized_log_entry() -> None:
    parser = LogParser()

    result = parser.parse("192.168.1.10 get /api/users 201")

    assert result == {
        "ip": "192.168.1.10",
        "method": "GET",
        "uri": "/api/users",
        "status_code": 201,
    }


@pytest.mark.asyncio
async def test_parse_rejects_invalid_uri() -> None:
    parser = LogParser()

    with pytest.raises(HTTPException) as error:
        parser.parse("192.168.1.10 GET api/users 200")

    assert error.value.status_code == 400
    assert error.value.detail == "URI value error"


@pytest.mark.asyncio
async def test_parse_rejects_ipv6_address() -> None:
    parser = LogParser()

    with pytest.raises(HTTPException) as error:
        parser.parse("2001:db8::1 GET /api/users 200")

    assert error.value.status_code == 400
    assert error.value.detail == "Only IPv4 is supported"
