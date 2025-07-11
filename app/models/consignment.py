from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime
from .base import TimestampMixin


class ConsignmentStatus(str, Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    LOST = "lost"
    DELIVERY_FAILED = "delivery_failed"
    RETURNED = "returned"


class ConsignmentBase(BaseModel):
    sender_name: str
    sender_phone: str
    sender_address: str
    receiver_name: str
    receiver_phone: str
    receiver_address: str
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    value: Optional[float] = None


class ConsignmentCreate(ConsignmentBase):
    current_warehouse_id: str
    destination_warehouse_id: str


class ConsignmentUpdate(BaseModel):
    current_warehouse_id: Optional[str] = None
    destination_warehouse_id: Optional[str] = None
    status: Optional[ConsignmentStatus] = None
    assigned_to: Optional[str] = None


class ConsignmentResponse(ConsignmentBase, TimestampMixin):
    id: str
    tracking_number: str
    current_warehouse_id: str
    destination_warehouse_id: str
    status: ConsignmentStatus
    assigned_to: Optional[str] = None
    delivered_at: Optional[datetime] = None


class ConsignmentStatusUpdate(BaseModel):
    status: ConsignmentStatus
    notes: Optional[str] = None


class ConsignmentTransfer(BaseModel):
    to_warehouse_id: str
    notes: Optional[str] = None


class ConsignmentAssign(BaseModel):
    assigned_to: str
    notes: Optional[str] = None
