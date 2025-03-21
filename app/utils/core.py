import logging
import re
import unicodedata

from fastapi import Depends
from pydantic import BaseModel
from time import perf_counter_ns
from typing import Annotated
from fastapi.requests import Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import text

from psutil import (
    cpu_percent,
    virtual_memory
)

from ..database import get_session
from .cache import read_cache
from ..configs import core_configs

logger = logging.getLogger(core_configs.logger_name)


async def get_api_uptime(request: Request) -> str:
    start_time_ns = request.app.state.start_time_ns
    elapsed_ns = perf_counter_ns() - start_time_ns
    elapsed_seconds = elapsed_ns / 1_000_000_000

    # Calculate days, hours, minutes, and seconds
    days = int(elapsed_seconds // 86400)  # 86400 seconds in a day
    hours = int((elapsed_seconds % 86400) // 3600)  # 3600 seconds in an hour
    minutes = int((elapsed_seconds % 3600) // 60)  # 60 seconds in a minute
    seconds = int(elapsed_seconds % 60)  # Remaining seconds

    # Format the result
    formatted_time = f'{days} days, {hours} hours, {minutes} minutes, {seconds} seconds'
    return formatted_time


async def get_system_metrics() -> dict:
    return {
        'cpu_usage': f'{cpu_percent()}%',
        'memory_usage': f'{virtual_memory().percent}%'
    }


async def get_db_response_time_ms(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    r = await session.execute(text('SELECT 1'))
    r.one_or_none()
    duration_ns = read_cache(request.state.request_id)

    if duration_ns is not None:
        duration_ms: float = duration_ns / 1_000_000
        return f'{duration_ms:.2} ms'

    return duration_ns


def json_encode_response_model(response: BaseModel) -> dict:
    return jsonable_encoder(
        obj=response,
        exclude_none=True
    )


def clean_text(text: str) -> str:
    return ' '.join((
        unicodedata
        .normalize('NFKD', re.sub(r'[^a-zA-Z0-9\s]', ' ', text))
        .encode('ASCII', 'ignore')
        .decode('ASCII')
        .lower()
        .strip()
        .split()
    ))
