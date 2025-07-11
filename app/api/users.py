from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.models.user import UserCreate, UserUpdate, UserResponse
from app.models.base import BaseResponse, PaginatedResponse
from app.services.user_service import UserService
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse)
async def create_user(
        user: UserCreate,
        current_user: dict = Depends(get_current_user)
):
    """Create a new user"""
    if current_user["role"] not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    return await UserService.create_user(user)


@router.get("/", response_model=PaginatedResponse)
async def get_users(
        warehouse_id: Optional[str] = Query(None),
        role: Optional[str] = Query(None),
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        current_user: dict = Depends(get_current_user)
):
    """Get paginated list of users"""
    if current_user["role"] not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    return await UserService.get_users(warehouse_id, role, page, page_size)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(**current_user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
        user_id: str,
        current_user: dict = Depends(get_current_user)
):
    """Get user by ID"""
    if current_user["role"] not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    user = await UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
        user_id: str,
        user: UserUpdate,
        current_user: dict = Depends(get_current_user)
):
    """Update user"""
    if current_user["role"] not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    updated_user = await UserService.update_user(user_id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.delete("/{user_id}", response_model=BaseResponse)
async def delete_user(
        user_id: str,
        current_user: dict = Depends(get_current_user)
):
    """Delete user"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    success = await UserService.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    return BaseResponse(message="User deleted successfully")


@router.post("/{user_id}/toggle-status", response_model=BaseResponse)
async def toggle_user_status(
        user_id: str,
        current_user: dict = Depends(get_current_user)
):
    """Toggle user active status"""
    if current_user["role"] not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    success = await UserService.toggle_user_status(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    return BaseResponse(message="User status updated successfully")