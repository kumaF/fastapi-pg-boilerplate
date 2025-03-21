from typing import Literal
from pydantic import (
    BaseModel,
    Field,
    model_validator,
    ConfigDict
)

from .user import UserCredentials
from .enums import GrantType


class LoginRequest(BaseModel):
    grant_type: GrantType = Field(...)
    credentials: UserCredentials | None = Field(default=None)
    refresh_token: str | None = Field(default=None)

    @model_validator(mode='after')
    def validate_login_request(self):
        if self.grant_type == GrantType.PASSWORD and self.credentials is None:
            raise ValueError("The 'credentials' object is required when 'grant_type' is 'password'.")

        elif self.grant_type == GrantType.REFRESH_TOKEN and self.refresh_token is None:
            raise ValueError("The 'refresh_token' field is required when 'grant_type' is 'refresh_token'.")

        return self


class QueryParams(BaseModel):
    model_config = ConfigDict(
        extra='allow'
    )

    sort_by: str = Field(default='created_at')
    sort_order: Literal['asc', 'desc'] = Field(default='asc')
    page: int = Field(default=1)
    per_page: int = Field(default=10)
    is_deleted: bool | None = Field(default=None)
    is_hidden: bool | None = Field(default=None)
    is_verified: bool | None = Field(default=None)
    is_approved: bool | None = Field(default=None)
    status: list[int] | None = Field(default=None)
    type: int | None = Field(default=None)
    is_subcategory: bool | None = Field(default=None)
    # categories: list[]
    expand: bool | None = Field(default=None)
    q: str | None = Field(default=None)
