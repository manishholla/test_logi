from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class BaseResponse(BaseModel):
    success: bool = True
    message: str = "Operation successful"
    data: Optional[dict] = None


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int


class TimestampMixin(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
