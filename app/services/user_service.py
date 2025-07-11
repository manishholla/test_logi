from typing import List, Optional
from app.database import db, supabase
from app.models.user import UserCreate, UserUpdate, UserResponse
from app.models.base import PaginatedResponse
from app.core.auth import get_password_hash
from fastapi import HTTPException
import uuid


class UserService:
    @staticmethod
    async def create_user(user: UserCreate) -> UserResponse:
        """Create a new user"""
        try:
            # Create user in Supabase Auth
            auth_response = supabase.auth.admin.create_user({
                "email": user.email,
                "password": user.password,
                "email_confirm": True
            })

            if not auth_response.user:
                raise HTTPException(status_code=400, detail="Failed to create user in auth system")

            # Create user in our user_management table
            user_data = {
                "id": auth_response.user.id,
                "email": user.email,
                "full_name": user.full_name,
                "phone": user.phone,
                "role": user.role.value,
                "warehouse_id": user.warehouse_id,
                "is_active": True
            }

            response = supabase.table("user_management").insert(user_data).execute()

            if response.data:
                return UserResponse(**response.data[0])
            else:
                raise HTTPException(status_code=400, detail="Failed to create user record")

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error creating user: {str(e)}")

    @staticmethod
    async def get_user(user_id: str) -> Optional[UserResponse]:
        """Get user by ID"""
        try:
            response = supabase.table("user_management").select("*").eq("id", user_id).execute()

            if response.data:
                return UserResponse(**response.data[0])
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    @staticmethod
    async def get_users(
            warehouse_id: Optional[str] = None,
            role: Optional[str] = None,
            page: int = 1,
            page_size: int = 20
    ) -> PaginatedResponse:
        """Get paginated list of users"""
        try:
            query = supabase.table("user_management").select("*", count="exact")

            if warehouse_id:
                query = query.eq("warehouse_id", warehouse_id)

            if role:
                query = query.eq("role", role)

            # Get total count
            count_response = query.execute()
            total = count_response.count

            # Get paginated data
            offset = (page - 1) * page_size
            data_response = query.range(offset, offset + page_size - 1).execute()

            users = [UserResponse(**user) for user in data_response.data]

            return PaginatedResponse(
                items=users,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=(total + page_size - 1) // page_size
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error getting users: {str(e)}")

    @staticmethod
    async def update_user(user_id: str, user: UserUpdate) -> Optional[UserResponse]:
        """Update user"""
        try:
            update_data = user.dict(exclude_unset=True)

            if update_data:
                response = supabase.table("user_management").update(update_data).eq("id", user_id).execute()

                if response.data:
                    return UserResponse(**response.data[0])

            return await UserService.get_user(user_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error updating user: {str(e)}")

    @staticmethod
    async def delete_user(user_id: str) -> bool:
        """Soft delete user"""
        try:
            response = supabase.table("user_management").update({"is_active": False}).eq("id", user_id).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

    @staticmethod
    async def toggle_user_status(user_id: str) -> bool:
        """Toggle user active status"""
        try:
            # Get current user
            current_user = await UserService.get_user(user_id)
            if not current_user:
                return False

            # Toggle status
            new_status = not current_user.is_active
            response = supabase.table("user_management").update({"is_active": new_status}).eq("id", user_id).execute()

            return len(response.data) > 0
        except Exception as e:
            print(f"Error toggling user status: {e}")
            return False
