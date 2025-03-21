from fastapi import FastAPI
from pydantic import ValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import (
    RequestValidationError,
    HTTPException
)

from .configs import core_configs
from .middlewares import AddRequestIdMiddleware
from .utils.lifespan import lifespan
from .errors.error_handlers import (
    http_exception_handler,
    schema_validation_error_handler,
    request_validation_error_handler
)

from .routers import (
    HealthRouter,
    UserRouter,
    AuthRouter
)

_api_version: str = core_configs.api_version.split('.')[0]
api_prefix: str = f'/api/v{_api_version}'


app = FastAPI(
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, request_validation_error_handler)
app.add_exception_handler(ValidationError, schema_validation_error_handler)

app.add_middleware(AddRequestIdMiddleware)

app.include_router(HealthRouter, prefix=api_prefix)
app.include_router(AuthRouter, prefix=api_prefix)
app.include_router(UserRouter, prefix=api_prefix)
