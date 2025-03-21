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
    TIMESTAMP,
    SMALLINT,
    BIGINT,
    REAL
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from .base import Base

from .brand import BrandModel
from .category import CategoryModel
from .tag import TagModel

from ..schemas.enums import ProductStatus

if TYPE_CHECKING:
    from .business import BusinessLocationModel
    from .tag import TagProductRelationshipModel
    from .category import CategoryProductRelationshipModel


class ProductInventoryModel(Base):
    __tablename__ = 'products_inventory'
    __table_args__ = (
        UniqueConstraint('product_id', 'business_location_id'),
        {'schema': None}
    )

    id: Mapped[uuid.UUID] = mapped_column(
        type_=UUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        primary_key=True
    )
    business_location_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('business_locations.id')
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('products.id')
    )
    sku: Mapped[int] = mapped_column(
        type_=SMALLINT,
        nullable=False
    )
    quantity_in_stock: Mapped[int] = mapped_column(
        type_=BIGINT,
        nullable=False
    )
    currency: Mapped[str] = mapped_column(
        type_=TEXT,
        nullable=False
    )
    price: Mapped[float] = mapped_column(
        type_=REAL,
        nullable=False
    )
    status: Mapped[int] = mapped_column(
        type_=SMALLINT,
        nullable=False,
        server_default=text(str(ProductStatus.AVAILABLE.value))
    )
    is_featured: Mapped[bool] = mapped_column(
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

    business_location: Mapped['BusinessLocationModel'] = relationship(
        back_populates='product_inventories',
        lazy='joined',
        uselist=True
    )

    # secondary relationships for many-to-many mappings

    product: Mapped['ProductModel'] = relationship(
        back_populates='location_inventories',
        lazy='joined',
        uselist=True
    )


class ProductModel(Base):
    __tablename__ = 'products'
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
    product_code: Mapped[str] = mapped_column(
        type_=TEXT,
        nullable=False,
        unique=True,
        index=True
    )
    brand_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('brands.id'),
        nullable=True
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

    brand_profile: Mapped['BrandModel'] = relationship(
        back_populates='products',
        lazy='joined'
    )
    business_locations: Mapped[List['BusinessLocationModel']] = relationship(
        back_populates='products',
        secondary='products_inventory',
        lazy='select',
        viewonly=True,
        uselist=True
    )
    categories: Mapped[List['CategoryModel']] = relationship(
        back_populates='products',
        secondary='product_category_relationships',
        lazy='joined',
        viewonly=True,
        uselist=True
    )
    tags: Mapped[List['TagModel']] = relationship(
        back_populates='products',
        secondary='product_tag_relationships',
        lazy='joined',
        viewonly=True,
        uselist=True
    )

    # secondary relationships for many-to-many mappings

    location_inventories: Mapped[List['ProductInventoryModel']] = relationship(
        back_populates='product',
        lazy='select',
        uselist=True
    )

    category_relationships: Mapped[List['CategoryProductRelationshipModel']] = relationship(
        back_populates='product',
        lazy='select',
        uselist=True
    )

    tag_relationships: Mapped[List['TagProductRelationshipModel']] = relationship(
        back_populates='product',
        lazy='select',
        uselist=True
    )


__all__ = ['ProductModel', 'ProductInventoryModel']
