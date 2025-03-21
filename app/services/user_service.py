from uuid import UUID
from typing import Annotated
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi import (
    Depends,
    HTTPException,
    Request,
    Query
)

from starlette.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY
)

from sqlalchemy import (
    select,
    update,
    and_,
    func,
    asc,
    desc
)

from ..utils.errors import handle_db_errors
from ..database import get_session
from ..models.user import UserModel
from ..schemas.request import QueryParams
from ..schemas.response import (
    ResponseModel,
    ResponseLinkModel,
    ResponsePaginationModel
)

from ..schemas.enums import (
    UserType,
    UserStatus
)

from ..schemas.user import (
    SignupUser,
    User,
    OutUser,
    UpdateUser
)

from ..utils.security import hash_password
from ..services.auth_service import (
    validate_access_token,
    identity_required
)


async def __get_user_by_id(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: UUID,
    is_deleted: bool | None
) -> UserModel:
    where_args = [UserModel.id == user_id]

    if is_deleted is not None:
        where_args.append(UserModel.is_deleted == is_deleted)

    statement = (
        select(UserModel)
        .where(
            *where_args
        )
    )

    try:
        results = await session.scalars(statement)
        db_user = results.one_or_none()
    except SQLAlchemyError as e:
        err = await handle_db_errors(e)
        return ResponseModel(
            status=err.status_code,
            success=False,
            message=err.message,
            errors=err.errors
        )

    if db_user is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail='Invalid user_id'
        )

    return db_user


async def __update_user_by_id(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: UUID,
    user: UpdateUser
) -> ResponseModel:
    user_dict = user.model_dump(
        mode='json',
        exclude_unset=True
    )

    if not bool(user_dict):
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Data provided is invalid or cannot be processed.'
        )

    db_user = await __get_user_by_id(
        session=session,
        user_id=user_id,
        is_deleted=False
    )

    statement = (
        update(UserModel)
        .where(UserModel.id == db_user.id)
        .values(user_dict)
    )

    try:
        await session.execute(statement)
        await session.commit()
        await session.refresh(db_user)
    except SQLAlchemyError as e:
        err = await handle_db_errors(e)
        return ResponseModel(
            status=err.status_code,
            success=False,
            message=err.message,
            errors=err.errors
        )

    return ResponseModel(
        status=HTTP_200_OK,
        success=True,
        message='User updated successfully.',
        payload={
            'id': db_user.id
        }
    )


async def create_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    user: SignupUser
) -> ResponseModel:
    user_dict = user.model_dump(mode='json')
    user_dict.update({
        'type': UserType.ADMIN,
        'password': await hash_password(user.password)
    })

    validated_user = User.model_validate(user_dict, from_attributes=True)
    db_user = UserModel(**validated_user.model_dump(mode='json'))

    try:
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
    except SQLAlchemyError as e:
        err = await handle_db_errors(e)
        return ResponseModel(
            status=err.status_code,
            success=False,
            message=err.message,
            errors=err.errors
        )

    return ResponseModel(
        status=HTTP_200_OK,
        success=True,
        message='User created successfully.',
        payload={
            'id': db_user.id
        }
    )


@identity_required([UserType.ADMIN])
async def fetch_all_users(
    request: Request,
    query_params: Annotated[QueryParams, Query()],
    session: Annotated[AsyncSession, Depends(get_session)],
    token_returns: Annotated[tuple[dict, dict], Depends(validate_access_token)]
) -> ResponseModel:
    payload = token_returns[0]

    where_args = []
    order_func = asc if query_params.sort_order == 'asc' else desc
    order_column = getattr(UserModel, query_params.sort_by, None)
    offset = (query_params.page - 1) * query_params.per_page
    limit = query_params.per_page

    if order_column is None:
        raise ValueError(f'Invalid column name: {query_params.sort_by}')

    if query_params.is_deleted is not None:
        where_args.append(UserModel.is_deleted == query_params.is_deleted)

    statement = (
        select(UserModel)
        .where(
            *where_args
        ).order_by(
            order_func(order_column)
        )
    )

    try:
        result_count = await session.scalar(select(func.count()).select_from(statement))

        statement = statement.offset(offset).limit(limit)
        results = await session.scalars(statement)
        db_users = results.all()
    except SQLAlchemyError as e:
        err = await handle_db_errors(e)
        return ResponseModel(
            status=err.status_code,
            success=False,
            message=err.message,
            errors=err.errors
        )

    db_users = [OutUser.model_validate({
        **user.to_dict(),
        'current_user_id': UUID(payload['id'])
    }) for user in db_users]

    return ResponseModel.create_model(
        status=HTTP_200_OK,
        payload=db_users,
        result_count=result_count,
        request=request,
        query_params=query_params
    )


@identity_required([UserType.ADMIN])
async def fetch_user_by_id(
    query_params: Annotated[QueryParams, Query()],
    session: Annotated[AsyncSession, Depends(get_session)],
    token_returns: Annotated[tuple[dict, dict], Depends(validate_access_token)],
    user_id: UUID
) -> ResponseModel:
    payload = token_returns[0]

    db_user = await __get_user_by_id(
        session=session,
        user_id=user_id,
        is_deleted=query_params.is_deleted
    )

    db_user = OutUser.model_validate({
        **db_user.to_dict(),
        'current_user_id': UUID(payload['id'])
    })

    return ResponseModel(
        status=HTTP_200_OK,
        success=True,
        payload=db_user.model_dump(mode='json')
    )


async def fetch_current_user(
    query_params: Annotated[QueryParams, Query()],
    session: Annotated[AsyncSession, Depends(get_session)],
    token_returns: Annotated[tuple[dict, dict], Depends(validate_access_token)]
) -> ResponseModel:
    payload = token_returns[0]

    db_user = await __get_user_by_id(
        session=session,
        user_id=payload['id'],
        is_deleted=query_params.is_deleted
    )

    db_user = OutUser.model_validate({
        **db_user.to_dict(),
        'current_user_id': UUID(payload['id'])
    })

    return ResponseModel(
        status=HTTP_200_OK,
        success=True,
        payload=db_user.model_dump(mode='json')
    )


async def current_user_update(
    session: Annotated[AsyncSession, Depends(get_session)],
    token_returns: Annotated[tuple[dict, dict], Depends(validate_access_token)],
    user: UpdateUser
) -> ResponseModel:
    payload: dict = token_returns[0]

    return await __update_user_by_id(
        session=session,
        user_id=payload['id'],
        user=user
    )


@identity_required([UserType.ADMIN])
async def update_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    token_returns: Annotated[tuple[dict, dict], Depends(validate_access_token)],
    user_id: UUID,
    user: UpdateUser
) -> ResponseModel:
    return await __update_user_by_id(
        session=session,
        user_id=user_id,
        user=user
    )


async def delete_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    token_returns: Annotated[tuple[dict, dict], Depends(validate_access_token)],
    user_id: UUID
) -> ResponseModel:
    db_user = await __get_user_by_id(
        session=session,
        user_id=user_id,
        is_deleted=False
    )

    db_user.is_deleted = True
    db_user.status = UserStatus.INACTIVE.value

    try:
        await session.commit()
        await session.refresh(db_user)
    except SQLAlchemyError as e:
        err = await handle_db_errors(e)
        return ResponseModel(
            status=err.status_code,
            success=False,
            message=err.message,
            errors=err.errors
        )

    return ResponseModel(
        status=HTTP_200_OK,
        success=True,
        message='User removed successfully.'
    )


async def verify_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: UUID
) -> ResponseModel:
    db_user = await __get_user_by_id(
        session=session,
        user_id=user_id,
        is_deleted=False
    )

    db_user.is_verified = True
    db_user.status = UserStatus.ACTIVE.value

    try:
        await session.commit()
        await session.refresh(db_user)
    except SQLAlchemyError as e:
        err = await handle_db_errors(e)
        return ResponseModel(
            status=err.status_code,
            success=False,
            message=err.message,
            errors=err.errors
        )

    return ResponseModel(
        status=HTTP_200_OK,
        success=True,
        message='User verified successfully.'
    )
