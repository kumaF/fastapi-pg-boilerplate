from typing import Annotated
from fastapi import (
    APIRouter,
    Depends
)

from fastapi.responses import JSONResponse

from ..schemas.response import ResponseModel
from ..utils.core import json_encode_response_model
from ..services.auth_service import (
    generate_access_token,
    verify_access_token
)

router = APIRouter(
    prefix='/oauth',
    tags=['Authentication']
)


@router.post(path='/token')
async def generate_tokens(content: Annotated[ResponseModel, Depends(generate_access_token)]) -> JSONResponse:
    return JSONResponse(
        status_code=content.status,
        content=json_encode_response_model(content)
    )


@router.get(path='/auth')
async def verify_token(content: Annotated[ResponseModel, Depends(verify_access_token)]) -> JSONResponse:
    return JSONResponse(
        status_code=content.status,
        content=json_encode_response_model(content)
    )
