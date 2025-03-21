import jwt
import base64
import json
from functools import wraps
from uuid import UUID

from fastapi.security.oauth2 import OAuth2PasswordBearer
from uuid import uuid4
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import (
    Annotated,
    Callable
)

from datetime import (
    datetime,
    timedelta,
    timezone
)

from fastapi import (
    Depends,
    HTTPException
)

from jwt.exceptions import (
    InvalidTokenError,
    ExpiredSignatureError
)

from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_423_LOCKED
)

from sqlalchemy import (
    select,
    or_
)

from ..database import get_session
from ..models.user import UserModel as user
from ..schemas.response import ResponseModel
from ..schemas.request import LoginRequest
from ..utils.security import verify_password
from ..utils.errors import handle_db_errors
from ..configs.core import settings
from ..schemas.enums import (
    GrantType,
    UserStatus,
    UserType,
    TokenType
)

from ..schemas.user import (
    UserCredentials,
    User,
    OutUser
)

oauth2_schema = OAuth2PasswordBearer(tokenUrl='/oauth/token')


async def _decode_jwt_header(token: str) -> dict:
    try:
        header_encoded = token.split('.')[0]
        header_decoded = base64.urlsafe_b64decode(header_encoded + '==').decode('utf-8')
        header = json.loads(header_decoded)
        return dict(header)
    except (IndexError, ValueError, json.JSONDecodeError) as e:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail='Invalid JWT header.',
            headers={'WWW-Authenticate': 'Bearer'}
        )


async def _decode_token(token: str) -> tuple[dict, dict]:
    try:
        payload = jwt.decode(
            jwt=token,
            algorithms=[settings.token_algorithm],
            key=base64.b64decode(settings.public_key),
            audience=settings.token_audience,
            issuer=settings.token_issuer,
            options={
                'verify_signature': True,
                'require': ['exp', 'iat', 'nbf', 'iss', 'jti', 'aud']
            }
        )

        if payload.get('id') is None:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail='Invalid token',
                headers={'WWW-Authenticate': 'Bearer'}
            )

        header = await _decode_jwt_header(token)

        return payload, header
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail='Token has expired.',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail='Invalid token',
            headers={'WWW-Authenticate': 'Bearer'}
        )


async def _generate_tokens(data: dict) -> tuple[str, str]:
    access_token: str = await _generate_jwt_token(
        data=data,
        token_type=TokenType.ACCESS_TOKEN,
        exp_delta=settings.access_token_exp_delta
    )

    refresh_token: str = await _generate_jwt_token(
        data=data,
        token_type=TokenType.REFRESH_TOKEN,
        exp_delta=settings.refresh_token_exp_delta
    )

    return access_token, refresh_token


async def _generate_jwt_token(
    data: dict,
    token_type: TokenType,
    exp_delta: int | None = None
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=exp_delta)

    to_encode.update({
        'exp': expire,
        'nbf': datetime.now(timezone.utc),
        'iss': settings.token_issuer,
        'iat': datetime.now(timezone.utc),
        'sub': to_encode['id'],
        'aud': settings.token_audience,
        'jti': uuid4().hex
    })

    return jwt.encode(
        payload=to_encode,
        algorithm=settings.token_algorithm,
        key=base64.b64decode(settings.private_key),
        headers={'ttyp': token_type.value}
    )


async def _login_for_access_token(
    credentials: UserCredentials,
    session: Annotated[AsyncSession, Depends(get_session)]
) -> ResponseModel:
    statement = (
        select(user)
        .where(or_(
            user.email == credentials.identifier,
            user.username == credentials.identifier
        ))
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
            status_code=HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication credentials',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    verified, updated_pwd = await verify_password(
        password=credentials.password,
        hashed_password=db_user.password
    )

    if not verified:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication credentials',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    user_data = User.model_validate(db_user.to_dict())

    if not user_data.is_verified:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail='User account is not verified. Please verify your account to proceed.',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    if user_data.status == UserStatus.INACTIVE:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail='User account is inactive. Please contact support.',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    if user_data.status == UserStatus.SUSPENDED:
        raise HTTPException(
            status_code=HTTP_423_LOCKED,
            detail='User account is locked or suspended. Please contact support.',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    if updated_pwd is not None:
        db_user.password = updated_pwd

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

    to_encode: dict = {
        'id': str(db_user.id),
        'email': db_user.email,
        'identity_type': db_user.type
    }

    access_token, refresh_token = await _generate_tokens(data=to_encode)

    return ResponseModel(
        status=HTTP_200_OK,
        success=True,
        payload={
            'token_type': 'bearer',
            'access_token': access_token,
            'expires_in': settings.access_token_exp_delta,
            'refresh_token': refresh_token
        }
    )


async def validate_access_token(token: Annotated[str, Depends(oauth2_schema)]) -> tuple[dict, dict]:
    payload, header = await _decode_token(token)

    if not header.get('ttyp') == TokenType.ACCESS_TOKEN.value:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail='Invalid token',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    return payload, header


async def generate_access_token(
    session: Annotated[AsyncSession, Depends(get_session)],
    login_request: LoginRequest
) -> ResponseModel:
    if login_request.grant_type == GrantType.PASSWORD:
        response = await _login_for_access_token(
            credentials=login_request.credentials,
            session=session
        )

        return response

    if login_request.grant_type == GrantType.REFRESH_TOKEN:
        payload, header = await _decode_token(login_request.refresh_token)

        if header.get('ttyp') == TokenType.REFRESH_TOKEN.value:
            to_encode: dict = {
                'id': payload['id'],
                'email': payload['email'],
                'identity_type': payload['identity_type']
            }

            access_token, refresh_token = await _generate_tokens(data=to_encode)

            return ResponseModel(
                status=HTTP_200_OK,
                success=True,
                payload={
                    'token_type': 'bearer',
                    'access_token': access_token,
                    'expires_in': settings.access_token_exp_delta,
                    'refresh_token': refresh_token
                }
            )

    raise HTTPException(
        status_code=HTTP_400_BAD_REQUEST,
        detail='Invalid grant type or token',
        headers={'WWW-Authenticate': 'Bearer'}
    )


async def verify_access_token(
    session: Annotated[AsyncSession, Depends(get_session)],
    token_returns: Annotated[tuple[dict, dict], Depends(validate_access_token)]
) -> ResponseModel:
    payload = token_returns[0]

    statement = (
        select(user)
        .where(user.id == payload['id'])
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
            status_code=HTTP_401_UNAUTHORIZED,
            detail='Invalid token',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    user_data = OutUser.model_validate({
        **db_user.to_dict(),
        'current_user_id': UUID(payload['id'])
    })

    return ResponseModel(
        status=HTTP_200_OK,
        success=True,
        payload=user_data.model_dump(
            mode='json',
            exclude=['is_deleted', 'is_verified', 'created_at', 'updated_at']
        )
    )


def identity_required(required: list[UserType] | list = None):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            payload, _ = kwargs.get('token_returns', None)

            if required is not None and UserType(payload['identity_type']) not in required:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail='Invalid permission to access this resource',
                    headers={'WWW-Authenticate': 'Bearer'}
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


__all__ = ['generate_access_token', 'verify_access_token', 'validate_access_token', 'identity_required']
