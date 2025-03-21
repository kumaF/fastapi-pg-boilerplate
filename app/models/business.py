import uuid
from typing import (
    List,
    TYPE_CHECKING
)

from datetime import datetime
from sqlalchemy import (
    func,
    text,
    ForeignKey,
    UniqueConstraint,
    Index,
    Column
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

from .address import AddressBusinessLocationRelationshipModel
from .tag import TagBusinessLocationRelationshipModel
from .product import ProductInventoryModel
from .category import CategoryBusinessLocationRelationshipModel
from .service import ServiceProviderModel

from ..schemas.enums import BusinessStatus

if TYPE_CHECKING:
    from .address import AddressModel
    from .tag import TagModel
    from .product import ProductModel
    from .category import CategoryModel
    from .service import ServiceModel


class BusinessProfileModel(Base):
    __tablename__ = 'business_profiles'
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
        index=True
    )
    logo_url: Mapped[str | None] = mapped_column(
        type_=TEXT,
        nullable=True
    )
    status: Mapped[int] = mapped_column(
        type_=SMALLINT,
        nullable=False,
        server_default=text(str(BusinessStatus.OPERATIONAL.value))
    )
    is_approved: Mapped[bool] = mapped_column(
        type_=BOOLEAN,
        nullable=False,
        server_default=text('false')
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
    is_hidden: Mapped[bool] = mapped_column(
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
        back_populates='business_profile',
        lazy='joined'
    )


class BusinessLocationModel(Base):
    __tablename__ = 'business_locations'
    __table_args__ = (
        UniqueConstraint('business_id', 'name'),
        Index(
            'business_locations_business_id_is_primary_idx', 'business_id', 'is_primary', unique=True,
            postgresql_where=Column('is_primary')),
        {'schema': None})

    id: Mapped[uuid.UUID] = mapped_column(
        type_=UUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        primary_key=True
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('business_profiles.id')
    )
    name: Mapped[str] = mapped_column(
        type_=TEXT,
        nullable=False,
        index=True
    )
    description: Mapped[str | None] = mapped_column(
        type_=TEXT,
        nullable=True
    )
    phone: Mapped[str | None] = mapped_column(
        type_=TEXT,
        nullable=True,
        index=True
    )
    email: Mapped[str | None] = mapped_column(
        type_=TEXT,
        nullable=True,
        index=True
    )
    status: Mapped[int] = mapped_column(
        type_=SMALLINT,
        nullable=False,
        server_default=text(str(BusinessStatus.OPERATIONAL.value))
    )
    is_primary: Mapped[bool] = mapped_column(
        type_=BOOLEAN,
        nullable=False,
        server_default=text('false')
    )
    is_deleted: Mapped[bool] = mapped_column(
        type_=BOOLEAN,
        nullable=False,
        server_default=text('false')
    )
    is_hidden: Mapped[bool] = mapped_column(
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

    business_profile: Mapped['BusinessProfileModel'] = relationship(
        back_populates='business_locations',
        lazy='joined'
    )
    addresses: Mapped[List['AddressModel']] = relationship(
        back_populates='business_locations',
        secondary='business_address_relationships',
        lazy='joined',
        viewonly=True
    )
    tags: Mapped[List['TagModel']] = relationship(
        back_populates='business_locations',
        secondary='business_tag_relationships',
        lazy='joined',
        viewonly=True,
        uselist=True
    )
    categories: Mapped[List['CategoryModel']] = relationship(
        back_populates='business_locations',
        secondary='business_category_relationships',
        lazy='joined',
        viewonly=True,
        uselist=True
    )
    products: Mapped[List['ProductModel']] = relationship(
        back_populates='business_locations',
        secondary='products_inventory',
        lazy='select',
        viewonly=True,
        uselist=True
    )
    services: Mapped[List['ServiceModel']] = relationship(
        back_populates='business_locations',
        secondary='service_providers',
        lazy='select',
        viewonly=True,
        uselist=True
    )

    # secondary relationships for many-to-many mappings

    address_relationships: Mapped['AddressBusinessLocationRelationshipModel'] = relationship(
        back_populates='business_location',
        lazy='joined'
    )
    tag_relationships: Mapped['TagBusinessLocationRelationshipModel'] = relationship(
        back_populates='business_location',
        lazy='select',
        uselist=True,
        viewonly=True
    )
    category_relationships: Mapped['CategoryBusinessLocationRelationshipModel'] = relationship(
        back_populates='business_location',
        lazy='select',
        uselist=True,
        viewonly=True
    )
    product_inventories: Mapped['ProductInventoryModel'] = relationship(
        back_populates='business_location',
        lazy='select',
        uselist=True,
        viewonly=True
    )
    service_providers: Mapped['ServiceProviderModel'] = relationship(
        back_populates='business_location',
        lazy='select',
        uselist=True,
        viewonly=True
    )


__all__ = ['BusinessProfileModel', 'BusinessLocationModel']
