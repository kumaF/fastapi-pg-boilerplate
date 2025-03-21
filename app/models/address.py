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
    SMALLINT,
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
    from .business import (
        BusinessLocationModel
    )


class AddressBusinessLocationRelationshipModel(Base):
    __tablename__ = 'business_address_relationships'
    __table_args__ = (
        UniqueConstraint('address_id', 'business_location_id'),
        {'schema': None}
    )

    id: Mapped[uuid.UUID] = mapped_column(
        type_=UUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        primary_key=True
    )
    address_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('addresses.id'),
        primary_key=True
    )
    business_location_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('business_locations.id'),
        primary_key=True
    )
    address: Mapped['AddressModel'] = relationship(
        back_populates='business_location_relationships', lazy='joined'
    )
    business_location: Mapped['BusinessLocationModel'] = relationship(
        back_populates='address_relationships', lazy='joined'
    )


class AddressModel(Base):
    __tablename__ = 'addresses'
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
    po_box: Mapped[str] = mapped_column(
        type_=TEXT,
        nullable=False
    )
    sub_premise: Mapped[str | None] = mapped_column(
        type_=TEXT,
        nullable=True,
        index=True
    )
    premise: Mapped[str | None] = mapped_column(
        type_=TEXT,
        nullable=True,
        index=True
    )
    street: Mapped[str | None] = mapped_column(
        type_=TEXT,
        nullable=True,
        index=True
    )
    dependent_locality: Mapped[str | None] = mapped_column(
        type_=TEXT,
        nullable=True,
        index=True
    )
    locality: Mapped[str] = mapped_column(
        type_=TEXT,
        nullable=False,
        index=True
    )
    sub_administrative_area: Mapped[str] = mapped_column(
        type_=TEXT,
        nullable=False,
        index=True
    )
    administrative_area: Mapped[str] = mapped_column(
        type_=TEXT,
        nullable=False,
        index=True
    )
    country: Mapped[str] = mapped_column(
        type_=TEXT,
        nullable=False,
        index=True
    )
    postal_code: Mapped[str] = mapped_column(
        type_=TEXT,
        nullable=False,
        index=True
    )
    type: Mapped[int] = mapped_column(
        type_=SMALLINT,
        nullable=False
    )
    is_primary: Mapped[bool] = mapped_column(
        type_=BOOLEAN,
        nullable=False
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

    business_locations: Mapped[List['BusinessLocationModel']] = relationship(
        back_populates='addresses',
        secondary='business_address_relationships',
        lazy='joined',
        viewonly=True
    )

    # secondary relationships for many-to-many mappings

    business_location_relationships: Mapped['AddressBusinessLocationRelationshipModel'] = relationship(
        back_populates='address',
        lazy='joined'
    )


__all__ = ['AddressModel', 'AddressBusinessLocationRelationshipModel']
