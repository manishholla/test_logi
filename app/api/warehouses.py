from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.models.warehouse import WarehouseCreate, WarehouseUpdate, WarehouseResponse
from app.models.base import BaseResponse, PaginatedResponse
from app.services.warehouse_service import WarehouseService
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@router.post("/", response_model=WarehouseResponse)
async def create_warehouse(
        warehouse: WarehouseCreate,
        current_user: dict = Depends(get_current_user)
):
    """Create a new warehouse"""
    if current_user["role"] not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    return await WarehouseService.create_warehouse(warehouse)


@router.get("/", response_model=PaginatedResponse)
async def get_warehouses(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        current_user: dict = Depends(get_current_user)
):
    """Get paginated list of warehouses"""
    return await WarehouseService.get_warehouses(page, page_size)


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(
        warehouse_id: str,
        current_user: dict = Depends(get_current_user)
):
    """Get warehouse by ID"""
    warehouse = await WarehouseService.get_warehouse(warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse


@router.put("/{warehouse_id}", response_model=WarehouseResponse)
async def update_warehouse(
        warehouse_id: str,
        warehouse: WarehouseUpdate,
        current_user: dict = Depends(get_current_user)
):
    """Update warehouse"""
    if current_user["role"] not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    updated_warehouse = await WarehouseService.update_warehouse(warehouse_id, warehouse)
    if not updated_warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return updated_warehouse


@router.delete("/{warehouse_id}", response_model=BaseResponse)
async def delete_warehouse(
        warehouse_id: str,
        current_user: dict = Depends(get_current_user)
):
    """Delete warehouse"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    success = await WarehouseService.delete_warehouse(warehouse_id)
    if not success:
        raise HTTPException(status_code=404, detail="Warehouse not found")

    return BaseResponse(message="Warehouse deleted successfully")