from typing import List, Optional
from app.database import db
from app.models.consignment import (
    ConsignmentCreate, ConsignmentUpdate, ConsignmentResponse,
    ConsignmentStatus, ConsignmentStatusUpdate
)
from app.models.base import PaginatedResponse
from fastapi import HTTPException
import uuid
import secrets
import string


class ConsignmentService:
    @staticmethod
    def generate_tracking_number() -> str:
        """Generate unique tracking number"""
        letters = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(3))
        numbers = ''.join(secrets.choice(string.digits) for _ in range(9))
        return f"{letters}{numbers}"

    @staticmethod
    async def create_consignment(consignment: ConsignmentCreate) -> ConsignmentResponse:
        """Create new consignment"""
        consignment_id = str(uuid.uuid4())
        tracking_number = ConsignmentService.generate_tracking_number()

        query = """
        INSERT INTO consignments (
            id, tracking_number, sender_name, sender_phone, sender_address,
            receiver_name, receiver_phone, receiver_address, weight, dimensions,
            value, current_warehouse_id, destination_warehouse_id, status
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
        RETURNING *
        """

        try:
            result = await db.fetchrow(
                query,
                consignment_id,
                tracking_number,
                consignment.sender_name,
                consignment.sender_phone,
                consignment.sender_address,
                consignment.receiver_name,
                consignment.receiver_phone,
                consignment.receiver_address,
                consignment.weight,
                consignment.dimensions,
                consignment.value,
                consignment.current_warehouse_id,
                consignment.destination_warehouse_id,
                ConsignmentStatus.PENDING
            )
            return ConsignmentResponse(**dict(result))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error creating consignment: {str(e)}")

    @staticmethod
    async def get_consignment(consignment_id: str) -> Optional[ConsignmentResponse]:
        """Get consignment by ID"""
        query = "SELECT * FROM consignments WHERE id = $1"
        result = await db.fetchrow(query, consignment_id)

        if result:
            return ConsignmentResponse(**dict(result))
        return None

    @staticmethod
    async def get_consignment_by_tracking(tracking_number: str) -> Optional[ConsignmentResponse]:
        """Get consignment by tracking number"""
        query = "SELECT * FROM consignments WHERE tracking_number = $1"
        result = await db.fetchrow(query, tracking_number)

        if result:
            return ConsignmentResponse(**dict(result))
        return None

    @staticmethod
    async def get_consignments(
            warehouse_id: Optional[str] = None,
            status: Optional[ConsignmentStatus] = None,
            page: int = 1,
            page_size: int = 20
    ) -> PaginatedResponse:
        """Get paginated consignments with filters"""
        offset = (page - 1) * page_size

        # Build WHERE clause
        where_conditions = []
        params = []
        param_count = 1

        if warehouse_id:
            where_conditions.append(f"current_warehouse_id = ${param_count}")
            params.append(warehouse_id)
            param_count += 1

        if status:
            where_conditions.append(f"status = ${param_count}")
            params.append(status.value)
            param_count += 1

        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

        # Count query
        count_query = f"SELECT COUNT(*) FROM consignments {where_clause}"
        total = await db.fetchrow(count_query, *params)

        # Data query
        query = f"""
        SELECT * FROM consignments 
        {where_clause}
        ORDER BY created_at DESC 
        LIMIT ${param_count} OFFSET ${param_count + 1}
        """
        params.extend([page_size, offset])

        results = await db.fetch(query, *params)
        consignments = [ConsignmentResponse(**dict(row)) for row in results]

        return PaginatedResponse(
            items=consignments,
            total=total['count'],
            page=page,
            page_size=page_size,
            total_pages=(total['count'] + page_size - 1) // page_size
        )

    @staticmethod
    async def update_consignment_status(
            consignment_id: str,
            status_update: ConsignmentStatusUpdate,
            user_id: str
    ) -> Optional[ConsignmentResponse]:
        """Update consignment status"""
        # Get current consignment
        current = await ConsignmentService.get_consignment(consignment_id)
        if not current:
            return None

        # Update consignment
        query = """
        UPDATE consignments 
        SET status = $1, updated_at = NOW()
        WHERE id = $2
        RETURNING *
        """

        result = await db.fetchrow(query, status_update.status.value, consignment_id)

        if result:
            # Log status change
            await ConsignmentService.log_status_change(
                consignment_id, current.status, status_update.status, user_id, status_update.notes
            )
            return ConsignmentResponse(**dict(result))
        return None

    @staticmethod
    async def log_status_change(
            consignment_id: str,
            from_status: ConsignmentStatus,
            to_status: ConsignmentStatus,
            user_id: str,
            notes: Optional[str] = None
    ):
        """Log consignment status changes"""
        query = """
        INSERT INTO consignment_status_log (
            consignment_id, from_status, to_status, changed_by, notes
        ) VALUES ($1, $2, $3, $4, $5)
        """

        await db.execute(
            query,
            consignment_id,
            from_status.value,
            to_status.value,
            user_id,
            notes
        )