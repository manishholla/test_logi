from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta
from app.services.dashboard_service import DashboardService
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
        warehouse_id: Optional[str] = Query(None),
        current_user: dict = Depends(get_current_user)
):
    """Get dashboard statistics"""
    # If user is not admin/manager, filter by their warehouse
    if current_user["role"] not in ["admin", "manager"]:
        warehouse_id = current_user["warehouse_id"]

    return await DashboardService.get_dashboard_stats(warehouse_id)


@router.get("/consignments-by-status")
async def get_consignments_by_status(
        warehouse_id: Optional[str] = Query(None),
        days: int = Query(30, ge=1, le=365),
        current_user: dict = Depends(get_current_user)
):
    """Get consignments grouped by status"""
    if current_user["role"] not in ["admin", "manager"]:
        warehouse_id = current_user["warehouse_id"]

    return await DashboardService.get_consignments_by_status(warehouse_id, days)


@router.get("/recent-activities")
async def get_recent_activities(
        warehouse_id: Optional[str] = Query(None),
        limit: int = Query(10, ge=1, le=50),
        current_user: dict = Depends(get_current_user)
):
    """Get recent activities"""
    if current_user["role"] not in ["admin", "manager"]:
        warehouse_id = current_user["warehouse_id"]

    return await DashboardService.get_recent_activities(warehouse_id, limit)


@router.get("/performance-metrics")
async def get_performance_metrics(
        warehouse_id: Optional[str] = Query(None),
        days: int = Query(30, ge=1, le=365),
        current_user: dict = Depends(get_current_user)
):
    """Get performance metrics"""
    if current_user["role"] not in ["admin", "manager"]:
        warehouse_id = current_user["warehouse_id"]

    return await DashboardService.get_performance_metrics(warehouse_id, days)


@router.get("/delivery-trends")
async def get_delivery_trends(
        warehouse_id: Optional[str] = Query(None),
        days: int = Query(30, ge=1, le=365),
        current_user: dict = Depends(get_current_user)
):
    """Get delivery trends over time"""
    if current_user["role"] not in ["admin", "manager"]:
        warehouse_id = current_user["warehouse_id"]

    return await DashboardService.get_delivery_trends(warehouse_id, days)