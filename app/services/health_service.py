from fastapi import Depends
from typing import Annotated
from starlette.status import HTTP_200_OK
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import text, Engine

from ..configs import core_configs
from ..database import get_session
from ..schemas.response import ResponseModel
from ..utils.core import (
    get_api_uptime,
    get_system_metrics,
    get_db_response_time_ms
)


async def health_check(
    session: Annotated[AsyncSession, Depends(get_session)],
    uptime: Annotated[str, Depends(get_api_uptime)],
    system_metrics: Annotated[dict, Depends(get_system_metrics)],
    db_response_time: Annotated[float, Depends(get_db_response_time_ms)]
) -> ResponseModel:
    return ResponseModel(
        status=HTTP_200_OK,
        success=True,
        payload={
            'api': 'healthy',
            'version': core_configs.api_version,
            'uptime': uptime,
            'system_metrics': system_metrics,
            'dependencies': {
                'database': {
                    'status': 'healthy' if session.is_active else 'unhealthy',
                    'response_time_ms': db_response_time
                }
            }
        }
    )
