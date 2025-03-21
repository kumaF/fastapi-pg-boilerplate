from typing import Annotated
from fastapi import (
    APIRouter,
    Depends
)

from fastapi.responses import JSONResponse

from ..services.health_service import health_check
from ..schemas.response import ResponseModel
from ..utils.core import json_encode_response_model

router = APIRouter(
    prefix='/health',
    tags=['Application Health']
)


@router.get(path='')
async def check_health(content: Annotated[ResponseModel, Depends(health_check)]) -> JSONResponse:
    return JSONResponse(
        status_code=content.status,
        content=json_encode_response_model(content)
    )
