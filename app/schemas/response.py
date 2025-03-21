from fastapi.requests import Request
from starlette.status import HTTP_200_OK
from math import ceil
from typing_extensions import Self
from pydantic import (
    BaseModel,
    Field,
    computed_field,
    AnyUrl
)

from urllib.parse import (
    urlencode,
    urlparse,
    parse_qs,
    urlunparse
)

from datetime import (
    datetime,
    timezone
)

from ..utils.request import get_request_id
from .request import QueryParams


class ResponsePaginationModel(BaseModel):
    current_page: int = Field(default=1)
    per_page: int = Field(default=10)
    total_items: int = Field(ge=0)

    @computed_field
    @property
    def total_pages(self) -> int:
        if self.total_items == 0:
            return 0

        return ceil(self.total_items / self.per_page)

    @computed_field
    @property
    def next_page(self) -> int | None:
        if self.current_page + 1 > self.total_pages:
            return None

        return self.current_page + 1

    @computed_field
    @property
    def previous_page(self) -> int | None:
        if self.current_page - 1 < 1:
            return None

        return self.current_page - 1


class ResponseMetaModel(BaseModel):
    sort_by: str | None = Field(default=None)
    sort_order: str | None = Field(default=None)
    filters: dict | None = Field(default=None)


class ResponseLinkModel(BaseModel):
    pagination: ResponsePaginationModel = Field(exclude=True)
    url: AnyUrl = Field(exclude=True)

    @staticmethod
    def update_query_params(url: AnyUrl, updated_query_params: dict) -> AnyUrl:
        parsed_url = urlparse(str(url))
        query_params = parse_qs(parsed_url.query)

        query_params.update(updated_query_params)

        updated_query = urlencode(query_params, doseq=True)
        updated_url = parsed_url._replace(query=updated_query)

        return AnyUrl(urlunparse(updated_url))

    @computed_field
    @property
    def first(self) -> AnyUrl | None:
        if self.pagination.total_pages < 1:
            return None

        return self.update_query_params(
            self.url,
            updated_query_params={
                'page': 1,
                'per_page': self.pagination.per_page
            }
        )

    @computed_field
    @property
    def last(self) -> AnyUrl | None:
        if self.pagination.total_pages < 2:
            return None

        return self.update_query_params(
            self.url,
            updated_query_params={
                'page': self.pagination.total_pages,
                'per_page': self.pagination.per_page
            }
        )

    @computed_field
    @property
    def next(self) -> AnyUrl | None:
        if self.pagination.next_page is None:
            return None

        return self.update_query_params(
            self.url,
            updated_query_params={
                'page': self.pagination.next_page,
                'per_page': self.pagination.per_page
            }
        )

    @computed_field
    @property
    def previous(self) -> AnyUrl | None:
        if self.pagination.previous_page is None:
            return None

        return self.update_query_params(
            self.url,
            updated_query_params={
                'page': self.pagination.previous_page,
                'per_page': self.pagination.per_page
            }
        )


class ResponseModel(BaseModel):
    status: int
    success: bool
    payload: dict | list | None = Field(default=None)
    message: str | None = Field(default=None)
    errors: list | None = Field(default=None)
    pagination: ResponsePaginationModel | None = Field(default=None)
    links: ResponseLinkModel | None = Field(default=None)
    meta: ResponseMetaModel | None = Field(default=None)
    request_id: str = Field(default_factory=get_request_id)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @classmethod
    def create_model(
        cls,
        request: Request,
        query_params: QueryParams,
        status: int = HTTP_200_OK,
        success: bool = True,
        payload: dict | list | None = None,
        message: str | None = None,
        errors: list | None = None,
        result_count: int = 0

    ) -> Self:
        pagination_model = ResponsePaginationModel(
            total_items=result_count,
            current_page=query_params.page,
            per_page=query_params.per_page
        )

        links_model = ResponseLinkModel(
            pagination=pagination_model,
            url=str(request.url)
        )

        meta_model = ResponseMetaModel(
            sort_by=query_params.sort_by,
            sort_order=query_params.sort_order,
            filters=query_params.model_dump(
                mode='json',
                exclude=[
                    'sort_by',
                    'sort_order',
                    'page',
                    'per_page'
                ]
            )
        )

        return ResponseModel(
            status=status,
            success=success,
            payload=payload,
            message=message,
            errors=errors,
            pagination=pagination_model,
            links=links_model,
            meta=meta_model
        )
