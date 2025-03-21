import uuid
from datetime import datetime
from typing import (
    List,
    TYPE_CHECKING
)

from sqlalchemy import (
    func,
    text,
    ForeignKey,
    UniqueConstraint
)

from sqlalchemy.dialects.postgresql import (
    UUID,
    TEXT,
    BOOLEAN,
    TIMESTAMP
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from .base import Base

if TYPE_CHECKING:
    from .product import ProductModel


class BrandModel(Base):
    __tablename__ = 'brands'
    __table_args__ = (
        {'schema': None}
    )

    id: Mapped[uuid.UUID] = mapped_column(
        type_=UUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        primary_key=True
    )
    name: Mapped[str] = mapped_column(
        type_=TEXT,
        nullable=False,
        unique=True,
        index=True
    )
    description: Mapped[str] = mapped_column(
        type_=TEXT,
        nullable=True
    )
    is_approved: Mapped[bool] = mapped_column(
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

    # relationships

    products: Mapped[List['ProductModel']] = relationship(
        back_populates='brand_profile',
        lazy='joined'
    )


__all__ = ['BrandModel']
