from pydantic import BaseModel, ConfigDict
from typing import Generic, TypeVar, List, Optional

T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PaginatedResponse(BaseSchema, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int


class HealthStatus(BaseSchema):
    status: str
    version: str = "1.0.0"
    database: bool
    redis: bool
    qdrant: bool
