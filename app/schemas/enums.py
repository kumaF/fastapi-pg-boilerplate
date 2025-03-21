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
class BusinessStatus(BaseEnum):
    TEMPORARY_CLOSED = 0
    OPERATIONAL = 1
    SUSPENDED = 2
    PERMANENTLY_CLOSED = 3


@unique
class ProductStatus(BaseEnum):
    OUT_OF_STOCK = 0
    AVAILABLE = 1
    DISCONTINUED = 2


@unique
class AddressType(BaseEnum):
    HOME = 0
    OFFICE = 1
    BILLING = 2
    SHIPPING = 3


@unique
class AssetType(BaseEnum):
    IMAGE = 0
    VIDEO = 1


@unique
class PositionType(BaseEnum):
    THUMBNAIL = 0
    LANDING = 1
    HEADER = 2
    FOOTER = 3
    LEFT_SIDEBAR = 4
    RIGHT_SIDEBAR = 5


@unique
class EntityType(BaseEnum):
    USER = 0
    BUSINESS = 1
    BUSINESS_LOCATION = 2
    PRODUCT = 3
    SERVICE = 4
    JOB = 5


@unique
class ServiceStatus(BaseEnum):
    INACTIVE = 0
    ACTIVE = 1
    DISCONTINUED = 2


@unique
class JobStatus(BaseEnum):
    CLOSED = 0
    OPEN = 1
    ARCHIVED = 2


@unique
class EmploymentType(BaseEnum):
    TEMPORARY = 0
    INTERNSHIP = 1
    FREELANCE = 2
    CONTRACT = 3
    PART_TIME = 4
    FULL_TIME = 5


@unique
class ExperienceLevel(BaseEnum):
    ENTRY = 0
    MID = 1
    SENIOR = 2
    LEAD = 3


@unique
class UserRole(BaseEnum):
    OWNER = 0


@unique
class CategoryType(BaseEnum):
    BUSINESS = 0
    PRODUCT = 1
    SERVICE = 2


@unique
class StockKeepingUnit(BaseEnum):
    PIECE = 0          # Individual items
    DOZEN = 1          # Group of 12 items
    GROSS = 2          # Group of 144 items (12 dozen)
    PAIR = 3           # Items sold in pairs
    SET = 4            # Bundled items
    GRAM = 5           # Small weight units
    KILOGRAM = 6       # Larger weight units
    MILLIGRAM = 7      # Very small weight units
    TONNE = 8          # Bulk weight
    MILLILITER = 9     # Small liquid volume
    LITER = 10         # Standard liquid volume
    CUBIC_METER = 11   # Bulk or industrial liquid volume
    METER = 12         # Length measurement
    CENTIMETER = 13    # Smaller length units
    INCH = 14          # Length in inches
    FOOT = 15          # Length in feet
    SQUARE_METER = 16  # Area measurement
    SQUARE_FOOT = 17   # Area measurement in feet
    HOUR = 18          # Time for labor/services
    DAY = 19           # Time for rentals/services
    PACKET = 20        # Predefined small quantity
    BOX = 21           # Packaged goods
    CRATE = 22         # Large packaging
    ROLL = 23          # Rolled items
    BOTTLE = 24        # Liquids in bottles
    CAN = 25           # Liquids/solids in cans

    @property
    def unit(self):
        unit_mapper: dict = {
            0: 'pcs',
            1: 'dozen',
            2: 'gross',
            3: 'pair(s)',
            4: 'set(s)',
            5: 'g',
            6: 'kg',
            7: 'mg',
            8: 't',
            9: 'ml',
            10: 'l',
            11: 'm³',
            12: 'm',
            13: 'cm',
            14: 'in',
            15: 'ft',
            16: 'm²',
            17: 'ft²',
            18: 'hr(s)',
            19: 'day(s)',
            20: 'packet(s)',
            21: 'box(es)',
            22: 'crate(s)',
            23: 'roll(s)',
            24: 'bottle(s)',
            25: 'can(s)'
        }

        return unit_mapper.get(self.value, self.name.lower())


IsoCurrency = BaseEnum('IsoCurrency', {str(currency.name).upper().replace(' ', '_'): str(
    currency.alpha_3).lower() for currency in currencies})
