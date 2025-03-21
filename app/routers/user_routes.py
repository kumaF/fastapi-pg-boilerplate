from typing import Annotated
from fastapi import (
    APIRouter,
    Depends
)

from fastapi.responses import JSONResponse

from ..schemas.response import ResponseModel
from ..utils.core import json_encode_response_model
from ..services.user_service import (
    create_user,
    fetch_all_users,
    fetch_current_user,
    current_user_update,
    fetch_user_by_id,
    update_user,
    delete_user,
    verify_user
)

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@router.post(path='')
async def user_creation(content: Annotated[ResponseModel, Depends(create_user)]) -> JSONResponse:
    return JSONResponse(
        status_code=content.status,
        content=json_encode_response_model(content)
    )


@router.get(path='')
async def get_all_users(content: Annotated[ResponseModel, Depends(fetch_all_users)]) -> JSONResponse:
    return JSONResponse(
        status_code=content.status,
        content=json_encode_response_model(content)
    )


@router.get(path='/me')
async def get_current_user(content: Annotated[ResponseModel, Depends(fetch_current_user)]) -> JSONResponse:
    return JSONResponse(
        status_code=content.status,
        content=json_encode_response_model(content)
    )


@router.patch(path='/me')
async def update_current_user(content: Annotated[ResponseModel, Depends(current_user_update)]) -> JSONResponse:
    return JSONResponse(
        status_code=content.status,
        content=json_encode_response_model(content)
    )


@router.get(path='/{user_id}')
async def get_user_by_id(content: Annotated[ResponseModel, Depends(fetch_user_by_id)]) -> JSONResponse:
    return JSONResponse(
        status_code=content.status,
        content=json_encode_response_model(content)
    )


@router.patch(path='/{user_id}')
async def user_update(content: Annotated[ResponseModel, Depends(update_user)]) -> JSONResponse:
    return JSONResponse(
        status_code=content.status,
        content=json_encode_response_model(content)
    )


@router.delete(path='/{user_id}')
async def remove_user(content: Annotated[ResponseModel, Depends(delete_user)]) -> JSONResponse:
    return JSONResponse(
        status_code=content.status,
        content=json_encode_response_model(content)
    )


@router.get(path='/{user_id}/verify')
async def temp_verify_user(content: Annotated[ResponseModel, Depends(verify_user)]) -> JSONResponse:
    return JSONResponse(
        status_code=content.status,
        content=json_encode_response_model(content)
    )
