import logging

from typing import Final

from contextvars import (
    ContextVar,
    Token
)

from ..configs import core_configs


logger = logging.getLogger(core_configs.logger_name)


REQUEST_ID_CTX_KEY: Final[str] = core_configs.request_id_ctx_key
_request_id_ctx_var: ContextVar[str | None] = ContextVar(REQUEST_ID_CTX_KEY, default=None)


async def set_request_id(request_id: str) -> Token:
    logger.info(f'Session context initialized for request handling: {request_id}')
    ctx_token = _request_id_ctx_var.set(request_id)
    return ctx_token


def get_request_id() -> str | None:
    return _request_id_ctx_var.get()


async def remove_request_id(token: Token) -> None:
    _request_id_ctx_var.reset(token)
