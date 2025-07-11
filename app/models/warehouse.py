from pydantic import BaseModel
from typing import Optional
from .base import TimestampMixin


class WarehouseBase(BaseModel):
    name: str
    address: str
    city: str
    state: str
    pincode: str
    phone: Optional[str] = None
    manager_id: Optional[str] = None


class WarehouseCreate(WarehouseBase):
    id: str


class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    manager_id: Optional[str] = None
    is_active: Optional[bool] = None


class WarehouseResponse(WarehouseBase, TimestampMixin):
    id: str
    is_active: bool
