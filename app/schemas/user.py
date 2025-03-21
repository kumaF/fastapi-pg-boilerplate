import re
from datetime import datetime

from pydantic import (
    Field,
    EmailStr,
    field_serializer,
    field_validator,
    computed_field
)

from uuid import (
    UUID,
    uuid4
)

from .base import Base
from .enums import (
    UserType,
    UserStatus
)

from ..configs import core_configs


class BaseUser(Base):
    username: str = Field(...)
    email: EmailStr = Field(...)


class SignupUser(BaseUser):
    password: str = Field(...)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str):
        if not re.match(core_configs.password_regex, v):
            raise ValueError(
                "Password must be at least 8 characters long, include an uppercase letter, "
                "a lowercase letter, a number, and a special character."
            )
        return v


class UserDTO(BaseUser):
    id: UUID = Field(default_factory=uuid4)
    type: UserType = Field(...)
    status: UserStatus = Field(default=UserStatus.INACTIVE)
    is_deleted: bool = Field(default=False)
    is_verified: bool = Field(default=False)
    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)


class User(UserDTO, SignupUser):
    pass


class OutUser(UserDTO):
    current_user_id: UUID = Field(exclude=True)

    @field_serializer('status', when_used='json')
    def serialize_status(self, v: UserStatus, _info):
        return {
            'value': v.value,
            'mapped': str(v.name).replace('_', ' ').title()
        }

    @field_serializer('type', when_used='json')
    def serialize_type(self, v: UserType, _info):
        return {
            'value': v.value,
            'mapped': str(v.name).replace('_', ' ').title()
        }

    @computed_field
    @property
    def is_current_user(self) -> bool:
        return self.id == self.current_user_id


class UserCredentials(Base):
    identifier: str = Field(...)
    password: str = Field(...)


class UpdateUser(Base):
    username: str | None = Field(default=None)
    email: EmailStr | None = Field(default=None)
    password: str | None = Field(default=None)
    status: UserStatus | None = Field(default=None)
    is_deleted: bool | None = Field(default=None)
    is_verified: bool | None = Field(default=None)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str | None):
        if v is not None and not re.match(core_configs.password_regex, v):
            raise ValueError(
                "Password must be at least 8 characters long, include an uppercase letter, "
                "a lowercase letter, a number, and a special character."
            )
        return v
