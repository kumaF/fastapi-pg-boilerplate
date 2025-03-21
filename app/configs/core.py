from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=('.env', '.env.local'),
        env_file_encoding='utf-8',
        extra='ignore',
        case_sensitive=True
    )

    token_algorithm: str = 'ES256'
    password_regex: str = r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$'

    api_version: str = Field(
        validation_alias='API_VERSION',
        default='1.0.0'
    )
    logger_name: str = Field(
        validation_alias='LOGGER_NAME',
        default='uvicorn'
    )
    request_id_ctx_key: str = Field(
        validation_alias='REQUEST_ID_CTX_KEY',
        default='request_id'
    )
    access_token_exp_delta: int = Field(
        validation_alias='ACCESS_TOKEN_EXP_DELTA',
        default=60*24  # in minutes
    )
    refresh_token_exp_delta: int = Field(
        validation_alias='REFRESH_TOKEN_EXP_DELTA',
        default=60*24*30  # in minutes
    )
    token_issuer: str = Field(
        validation_alias='TOKEN_ISSUER',
        default='auth:loongrid'
    )
    token_audience: str = Field(
        validation_alias='TOKEN_ISSUER',
        default='api:loongrid'
    )
    public_key: str = Field(
        validation_alias='PUBLIC_KEY'
    )
    private_key: str = Field(
        validation_alias='PRIVATE_KEY'
    )


settings = Settings()
