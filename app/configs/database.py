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

    db_host: str = Field(validation_alias='POSTGRES_HOST')
    db_port: str = Field(validation_alias='POSTGRES_PORT')
    db_user: str = Field(validation_alias='POSTGRES_USER')
    db_pw: str = Field(validation_alias='POSTGRES_PASSWORD')
    db_name: str = Field(validation_alias='POSTGRES_DB')


settings = Settings()
