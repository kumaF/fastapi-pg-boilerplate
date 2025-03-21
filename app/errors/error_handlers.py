from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from fastapi.exceptions import (
    HTTPException,
    RequestValidationError
)

from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from ..schemas.response import ResponseModel
from ..utils.core import json_encode_response_model


async def http_exception_handler(
    request: Request,
    e: HTTPException
) -> JSONResponse:
    content = ResponseModel(
        status=e.status_code,
        success=False,
        message=e.detail
    )

    return JSONResponse(
        status_code=content.status,
        content=json_encode_response_model(content),
        headers=e.headers
    )


async def schema_validation_error_handler(
    request: Request,
    e: ValidationError
) -> JSONResponse:
    content = ResponseModel(
        status=HTTP_422_UNPROCESSABLE_ENTITY,
        success=False,
        message=f'{e.title.lower()} model validation failed with {str(e.error_count())} errors.',
        errors=json_encode_response_model(e.errors())
    )

    return JSONResponse(
        status_code=content.status,
        content=json_encode_response_model(content)
    )


async def request_validation_error_handler(
    request: Request,
    e: RequestValidationError
) -> JSONResponse:
    content = ResponseModel(
        status=HTTP_422_UNPROCESSABLE_ENTITY,
        success=False,
        message=f'request body validation failed.',
        errors=json_encode_response_model(e.errors())
    )

    return JSONResponse(
        status_code=content.status,
        content=json_encode_response_model(content)
    )
