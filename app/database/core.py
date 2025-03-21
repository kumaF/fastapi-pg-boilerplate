import logging

from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from fastapi.exceptions import HTTPException
from typing import AsyncGenerator
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio.scoping import async_scoped_session
from sqlalchemy.ext.asyncio.session import (
    AsyncSession,
    async_sessionmaker
)

from sqlalchemy.ext.asyncio.engine import (
    AsyncEngine,
    create_async_engine
)

from ..utils.request import get_request_id
from ..configs import (
    core_configs,
    db_configs
)

logger = logging.getLogger(core_configs.logger_name)

url_object: URL = URL.create(
    drivername='postgresql+asyncpg',
    username=db_configs.db_user,
    password=db_configs.db_pw,
    host=db_configs.db_host,
    port=db_configs.db_port,
    database=db_configs.db_name
)

async_engine: AsyncEngine = create_async_engine(
    url=url_object,
    echo=False,
    future=True
)

async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Session = async_scoped_session(
    session_factory=async_session_factory,
    scopefunc=get_request_id
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    try:
        async with Session() as session:
            logger.info(f'Initialized database session for request: {get_request_id()}.')
            yield session
    except Exception as e:
        logger.error(f'Database error: {e}')

        if isinstance(e, HTTPException):
            raise HTTPException(
                status_code=e.status_code,
                detail=str(e)
            )

        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
