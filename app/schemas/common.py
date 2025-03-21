from pydantic import (
    BaseModel,
    Field
)


class DetailedError(BaseModel):
    status_code: int
    message: str
    errors: list = Field(default=None)
