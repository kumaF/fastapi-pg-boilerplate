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

from .category import CategoryModel
from .tag import TagModel

from ..schemas.enums import ServiceStatus

if TYPE_CHECKING:
    from .business import BusinessLocationModel
    from .tag import TagServiceRelationshipModel
    from .category import CategoryServiceRelationshipModel


class ServiceProviderModel(Base):
    __tablename__ = 'service_providers'
    __table_args__ = (
        UniqueConstraint('service_id', 'business_location_id'),
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
    service_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('services.id')
    )
    description: Mapped[str] = mapped_column(
        type_=TEXT,
        nullable=True
    )
    sku: Mapped[int] = mapped_column(
        type_=SMALLINT,
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
        server_default=text(str(ServiceStatus.ACTIVE.value))
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
        back_populates='service_providers',
        lazy='joined',
        uselist=True
    )

    service: Mapped['ServiceModel'] = relationship(
        back_populates='provider_locations',
        lazy='joined',
        uselist=True
    )


class ServiceModel(Base):
    __tablename__ = 'services'
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
        back_populates='services',
        secondary='service_providers',
        lazy='select',
        viewonly=True,
        uselist=True
    )

    categories: Mapped[List['CategoryModel']] = relationship(
        back_populates='services',
        secondary='service_category_relationships',
        lazy='joined',
        viewonly=True,
        uselist=True
    )

    tags: Mapped[List['TagModel']] = relationship(
        back_populates='services',
        secondary='service_tag_relationships',
        lazy='joined',
        viewonly=True,
        uselist=True
    )

    # secondary relationships for many-to-many mappings

    provider_locations: Mapped[List['ServiceProviderModel']] = relationship(
        back_populates='service',
        lazy='select',
        uselist=True
    )

    category_relationships: Mapped[List['CategoryServiceRelationshipModel']] = relationship(
        back_populates='service',
        lazy='select',
        uselist=True
    )

    tag_relationships: Mapped[List['TagServiceRelationshipModel']] = relationship(
        back_populates='service',
        lazy='select',
        uselist=True
    )


__all__ = ['ServiceModel', 'ServiceProviderModel']
