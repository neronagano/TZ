from typing import Annotated

from fastapi import APIRouter, Depends, status
from services.log_parser import get_parsed_log

router = APIRouter(prefix="/data", tags=["Data"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_log_entry(
    parsed_log: Annotated[dict[str, str | int], Depends(get_parsed_log)],
):
    return {"log": parsed_log}
