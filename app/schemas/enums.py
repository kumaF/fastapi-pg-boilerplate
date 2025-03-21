from pycountry import currencies
from typing import Literal
from enum import (
    Enum,
    unique
)


class BaseEnum(Enum):
    @classmethod
    def to_dict(cls, mode: Literal['python', 'json'] = 'python'):
        if mode == 'python':
            return {opt.name: opt.value for opt in cls}
        elif mode == 'json':
            return [{
                'name': opt.name,
                'name_param': getattr(opt, 'unit', opt.name).lower(),
                'name_pretty': opt.name.replace('_', ' ').title(),
                'value': opt.value
            } for opt in cls]

    @classmethod
    def to_list(cls, mode: Literal['python', 'json'] = 'python'):
        if mode == 'python':
            return [opt.value for opt in cls]
        elif mode == 'json':
            return [opt.name.lower() for opt in cls]


@unique
class TokenType(BaseEnum):
    ACCESS_TOKEN = 'access_token'
    REFRESH_TOKEN = 'refresh_token'


@unique
class GrantType(BaseEnum):
    PASSWORD = 'password'
    REFRESH_TOKEN = 'refresh_token'


@unique
class UserType(BaseEnum):
    ADMIN = 0
    BUSINESS = 1
    CUSTOMER = 2


@unique
class UserStatus(BaseEnum):
    INACTIVE = 0
    ACTIVE = 1
    SUSPENDED = 2


@unique
class UserRole(BaseEnum):
    OWNER = 0
