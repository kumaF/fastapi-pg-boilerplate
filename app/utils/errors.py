from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR
)

from sqlalchemy.exc import (
    DataError,
    IntegrityError,
    OperationalError,
    SQLAlchemyError
)

from ..schemas.common import DetailedError


async def handle_db_errors(e: SQLAlchemyError) -> DetailedError:
    if isinstance(e, DataError):
        return DetailedError(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            message='Incorrect data.',
            errors=[{'code': e.code, 'details': e._message()}]
        )
    elif isinstance(e, IntegrityError):
        return DetailedError(
            status_code=HTTP_409_CONFLICT,
            message='Duplicate entry',
            errors=[{'code': e.code, 'details': e._message()}]
        )
    elif isinstance(e, OperationalError):
        return DetailedError(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            message='Query failed due to lock/dead lock issues.',
            errors=[{'code': e.code, 'details': e._message()}]
        )
    else:
        return DetailedError(
            status_code=HTTP_400_BAD_REQUEST,
            message='Unexpected SQLAlchemy error.',
            errors=[{'code': e.code, 'details': e._message()}]
        )
