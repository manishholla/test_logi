from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.models.consignment import (
    ConsignmentCreate, ConsignmentUpdate, ConsignmentResponse,
    ConsignmentStatus, ConsignmentStatusUpdate
)
from app.models.base import BaseResponse, PaginatedResponse
from app.services.consignment_service import ConsignmentService
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/consignments", tags=["Consignments"])


@router.post("/", response_model=ConsignmentResponse)
async def create_consignment(
        consignment: ConsignmentCreate,
        current_user: dict = Depends(get_current_user)
):
    """Create new consignment"""
    return await ConsignmentService.create_consignment(consignment)


@router.get("/", response_model=PaginatedResponse)
async def get_consignments(
        warehouse_id: Optional[str] = Query(None),
        status: Optional[ConsignmentStatus] = Query(None),
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        current_user: dict = Depends(get_current_user)
):
    """Get paginated consignments with filters"""
    # Filter by user's warehouse if not admin
    if current_user["role"] not in ["admin", "manager"] and not warehouse_id:
        warehouse_id = current_user["warehouse_id"]

    return await ConsignmentService.get_consignments(warehouse_id, status, page, page_size)


@router.get("/{consignment_id}", response_model=ConsignmentResponse)
async def get_consignment(
        consignment_id: str,
        current_user: dict = Depends(get_current_user)
):
    """Get consignment by ID"""
    consignment = await ConsignmentService.get_consignment(consignment_id)
    if not consignment:
        raise HTTPException(status_code=404, detail="Consignment not found")
    return consignment


@router.get("/tracking/{tracking_number}", response_model=ConsignmentResponse)
async def track_consignment(tracking_number: str):
    """Track consignment by tracking number (public endpoint)"""
    consignment = await ConsignmentService.get_consignment_by_tracking(tracking_number)
    if not consignment:
        raise HTTPException(status_code=404, detail="Consignment not found")
    return consignment


@router.put("/{consignment_id}/status", response_model=ConsignmentResponse)
async def update_consignment_status(
        consignment_id: str,
        status_update: ConsignmentStatusUpdate,
        current_user: dict = Depends(get_current_user)
):
    """Update consignment status"""
    updated_consignment = await ConsignmentService.update_consignment_status(
        consignment_id, status_update, current_user["id"]
    )
    if not updated_consignment:
        raise HTTPException(status_code=404, detail="Consignment not found")
    return updated_consignment