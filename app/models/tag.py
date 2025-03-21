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
    from .business import BusinessLocationModel
    from .product import ProductModel
    from .service import ServiceModel


class TagBusinessLocationRelationshipModel(Base):
    __tablename__ = 'business_tag_relationships'
    __table_args__ = (
        UniqueConstraint('tag_id', 'business_location_id'),
        {'schema': None}
    )

    id: Mapped[uuid.UUID] = mapped_column(
        type_=UUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        primary_key=True
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('tags.id'),
        primary_key=True
    )
    business_location_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('business_locations.id'),
        primary_key=True
    )

    # relationships

    tag: Mapped['TagModel'] = relationship(
        back_populates='business_location_relationships',
        lazy='select',
        uselist=True
    )
    business_location: Mapped['BusinessLocationModel'] = relationship(
        back_populates='tag_relationships',
        lazy='select',
        uselist=True
    )


class TagProductRelationshipModel(Base):
    __tablename__ = 'product_tag_relationships'
    __table_args__ = (
        UniqueConstraint('tag_id', 'product_id'),
        {'schema': None}
    )

    id: Mapped[uuid.UUID] = mapped_column(
        type_=UUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        primary_key=True
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('tags.id'),
        primary_key=True
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('products.id'),
        primary_key=True
    )

    # relationships

    tag: Mapped['TagModel'] = relationship(
        back_populates='product_relationships',
        lazy='select',
        uselist=True
    )
    product: Mapped['ProductModel'] = relationship(
        back_populates='tag_relationships',
        lazy='select',
        uselist=True
    )


class TagServiceRelationshipModel(Base):
    __tablename__ = 'service_tag_relationships'
    __table_args__ = (
        UniqueConstraint('tag_id', 'service_id'),
        {'schema': None}
    )

    id: Mapped[uuid.UUID] = mapped_column(
        type_=UUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
        primary_key=True
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('tags.id'),
        primary_key=True
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('services.id'),
        primary_key=True
    )

    # relationships

    tag: Mapped['TagModel'] = relationship(
        back_populates='service_relationships',
        lazy='select',
        uselist=True
    )
    service: Mapped['ServiceModel'] = relationship(
        back_populates='tag_relationships',
        lazy='select',
        uselist=True
    )


class TagModel(Base):
    __tablename__ = 'tags'
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

    business_locations: Mapped[List['BusinessLocationModel']] = relationship(
        back_populates='tags',
        secondary='business_tag_relationships',
        lazy='select',
        viewonly=True,
        uselist=True
    )

    products: Mapped[List['ProductModel']] = relationship(
        back_populates='tags',
        secondary='product_tag_relationships',
        lazy='select',
        viewonly=True,
        uselist=True
    )

    services: Mapped[List['ServiceModel']] = relationship(
        back_populates='tags',
        secondary='service_tag_relationships',
        lazy='select',
        viewonly=True,
        uselist=True
    )

    # secondary relationships for many-to-many mappings

    business_location_relationships: Mapped[List['TagBusinessLocationRelationshipModel']] = relationship(
        back_populates='tag',
        lazy='select',
        uselist=True
    )

    product_relationships: Mapped[List['TagProductRelationshipModel']] = relationship(
        back_populates='tag',
        lazy='select',
        uselist=True
    )

    service_relationships: Mapped[List['TagServiceRelationshipModel']] = relationship(
        back_populates='tag',
        lazy='select',
        uselist=True
    )


__all__ = ['TagModel', 'TagBusinessLocationRelationshipModel',
           'TagProductRelationshipModel', 'TagServiceRelationshipModel']
