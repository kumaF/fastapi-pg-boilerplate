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
    SMALLINT
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from .base import Base

if TYPE_CHECKING:
    from .business import BusinessLocationModel
    from .product import ProductModel
    from .service import ServiceModel


class CategoryBusinessLocationRelationshipModel(Base):
    __tablename__ = 'business_category_relationships'
    __table_args__ = (
        UniqueConstraint('category_id', 'business_location_id'),
        {'schema': None}
    )

    id: Mapped[uuid.UUID] = mapped_column(
        type_=UUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        primary_key=True
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('categories.id'),
        primary_key=True
    )
    business_location_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('business_locations.id'),
        primary_key=True
    )

    # relationships

    category: Mapped['CategoryModel'] = relationship(
        back_populates='business_location_relationships',
        lazy='select',
        uselist=True
    )
    business_location: Mapped['BusinessLocationModel'] = relationship(
        back_populates='category_relationships',
        lazy='select',
        uselist=True
    )


class CategoryProductRelationshipModel(Base):
    __tablename__ = 'product_category_relationships'
    __table_args__ = (
        UniqueConstraint('category_id', 'product_id'),
        {'schema': None}
    )

    id: Mapped[uuid.UUID] = mapped_column(
        type_=UUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        primary_key=True
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('categories.id'),
        primary_key=True
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('products.id'),
        primary_key=True
    )

    # relationships

    category: Mapped['CategoryModel'] = relationship(
        back_populates='product_relationships',
        lazy='select',
        uselist=True
    )
    product: Mapped['ProductModel'] = relationship(
        back_populates='category_relationships',
        lazy='select',
        uselist=True
    )


class CategoryServiceRelationshipModel(Base):
    __tablename__ = 'service_category_relationships'
    __table_args__ = (
        UniqueConstraint('category_id', 'service_id'),
        {'schema': None}
    )

    id: Mapped[uuid.UUID] = mapped_column(
        type_=UUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        primary_key=True
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('categories.id'),
        primary_key=True
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('services.id'),
        primary_key=True
    )

    # relationships

    category: Mapped['CategoryModel'] = relationship(
        back_populates='service_relationships',
        lazy='select',
        uselist=True
    )
    service: Mapped['ServiceModel'] = relationship(
        back_populates='category_relationships',
        lazy='select',
        uselist=True
    )


class CategoryModel(Base):
    __tablename__ = 'categories'
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
    title: Mapped[str] = mapped_column(
        type_=TEXT,
        nullable=False,
        unique=True,
        index=True
    )
    type: Mapped[int] = mapped_column(
        type_=SMALLINT,
        nullable=False
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('categories.id'),
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

    category: Mapped['CategoryModel'] = relationship(
        back_populates='subcategories',
        lazy='select'
    )

    subcategories: Mapped[List['CategoryModel']] = relationship(
        back_populates='category',
        lazy='select',
        remote_side=[id]
    )

    business_locations: Mapped[List['BusinessLocationModel']] = relationship(
        back_populates='categories',
        secondary='business_category_relationships',
        lazy='select',
        viewonly=True,
        uselist=True
    )

    products: Mapped[List['ProductModel']] = relationship(
        back_populates='categories',
        secondary='product_category_relationships',
        lazy='select',
        viewonly=True,
        uselist=True
    )

    services: Mapped[List['ServiceModel']] = relationship(
        back_populates='categories',
        secondary='service_category_relationships',
        lazy='select',
        viewonly=True,
        uselist=True
    )

    # secondary relationships for many-to-many mappings

    business_location_relationships: Mapped[List['CategoryBusinessLocationRelationshipModel']] = relationship(
        back_populates='category',
        lazy='select',
        uselist=True
    )

    product_relationships: Mapped[List['CategoryProductRelationshipModel']] = relationship(
        back_populates='category',
        lazy='select',
        uselist=True
    )

    service_relationships: Mapped[List['CategoryServiceRelationshipModel']] = relationship(
        back_populates='category',
        lazy='select',
        uselist=True
    )


__all__ = ['CategoryModel', 'CategoryBusinessLocationRelationshipModel']
