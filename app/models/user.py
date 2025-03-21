import uuid

from datetime import datetime
from sqlalchemy import (
    func,
    text
)

from sqlalchemy.dialects.postgresql import (
    UUID,
    TEXT,
    SMALLINT,
    BOOLEAN,
    TIMESTAMP,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from .base import Base

from ..schemas.enums import UserStatus


class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(
        type_=UUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        primary_key=True
    )
    username: Mapped[str] = mapped_column(
        type_=TEXT,
        nullable=False,
        unique=True,
        index=True
    )
    email: Mapped[str] = mapped_column(
        type_=TEXT,
        nullable=False,
        unique=True,
        index=True
    )
    password: Mapped[str] = mapped_column(
        type_=TEXT,
        nullable=False
    )
    type: Mapped[int] = mapped_column(
        type_=SMALLINT,
        nullable=False
    )
    status: Mapped[int] = mapped_column(
        type_=SMALLINT,
        nullable=False,
        server_default=text(str(UserStatus.INACTIVE.value))
    )
    is_verified: Mapped[bool] = mapped_column(
        type_=BOOLEAN,
        nullable=False,
        server_default=text('false')
    )
    is_deleted: Mapped[bool] = mapped_column(
        type_=BOOLEAN,
        nullable=False,
        server_default=text('false')
    )
    created_at: Mapped[datetime] = mapped_column(
        type_=TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        type_=TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )


__all__ = ['UserModel']
