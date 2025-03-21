import logging

from fastapi import Request
from uuid import uuid4
from time import perf_counter_ns
from contextvars import Token
from starlette.middleware.base import BaseHTTPMiddleware

from ..configs import core_configs
from ..utils.request import (
    set_request_id,
    remove_request_id
)

logger = logging.getLogger(core_configs.logger_name)


class AddRequestIdMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        start_time_ns = perf_counter_ns()
        request_id: str = str(uuid4().hex)
        request.state.request_id = request_id
        ctx_token: Token = await set_request_id(request_id)
        logger.info(f'Start processing request: {request_id}')

        response = await call_next(request)

        await remove_request_id(ctx_token)
        duration_ns: int = perf_counter_ns() - start_time_ns
        duration_ms: float = duration_ns / 1_000_000
        logger.info(f'Finished processing request: {request_id} in {duration_ms:.4f} milliseconds')

        return response
