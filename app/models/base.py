from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.inspection import inspect

from ..database.constants import POSTGRES_INDEXES_NAMING_CONVENTION


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION,
        schema=None
    )

    __table_args__ = {
        'schema': None
    }

    def to_dict(
        self,
        include: list | None = None,
        exclude: list | None = None
    ):
        if bool(include) and not isinstance(include, list):
            raise TypeError("The 'include' argument must be a valid list or None")

        if bool(exclude) and not isinstance(exclude, list):
            raise TypeError("The 'exclude' argument must be a valid list or None")

        if bool(include) and bool(exclude):
            return {column.key: getattr(self, column.key) for column in inspect(self).mapper.column_attrs if column in include and column not in exclude}
        elif bool(include):
            return {column.key: getattr(self, column.key) for column in inspect(self).mapper.column_attrs if column in include}
        elif bool(exclude):
            return {column.key: getattr(self, column.key) for column in inspect(self).mapper.column_attrs if column not in exclude}
        else:
            return {column.key: getattr(self, column.key) for column in inspect(self).mapper.column_attrs}
