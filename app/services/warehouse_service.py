from typing import List, Optional
from app.database import db
from app.models.warehouse import WarehouseCreate, WarehouseUpdate, WarehouseResponse
from app.models.base import PaginatedResponse
from fastapi import HTTPException
import uuid


class WarehouseService:
    @staticmethod
    async def create_warehouse(warehouse: WarehouseCreate) -> WarehouseResponse:
        """Create a new warehouse"""
        query = """
        INSERT INTO warehouses (id, name, address, city, state, pincode, phone, manager_id)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING *
        """

        try:
            result = await db.fetchrow(
                query,
                warehouse.id,
                warehouse.name,
                warehouse.address,
                warehouse.city,
                warehouse.state,
                warehouse.pincode,
                warehouse.phone,
                warehouse.manager_id
            )
            return WarehouseResponse(**dict(result))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error creating warehouse: {str(e)}")

    @staticmethod
    async def get_warehouse(warehouse_id: str) -> Optional[WarehouseResponse]:
        """Get warehouse by ID"""
        query = "SELECT * FROM warehouses WHERE id = $1 AND is_active = true"
        result = await db.fetchrow(query, warehouse_id)

        if result:
            return WarehouseResponse(**dict(result))
        return None

    @staticmethod
    async def get_warehouses(page: int = 1, page_size: int = 20) -> PaginatedResponse:
        """Get paginated list of warehouses"""
        offset = (page - 1) * page_size

        # Get total count
        count_query = "SELECT COUNT(*) FROM warehouses WHERE is_active = true"
        total = await db.fetchrow(count_query)

        # Get warehouses
        query = """
        SELECT * FROM warehouses 
        WHERE is_active = true 
        ORDER BY created_at DESC 
        LIMIT $1 OFFSET $2
        """
        results = await db.fetch(query, page_size, offset)

        warehouses = [WarehouseResponse(**dict(row)) for row in results]

        return PaginatedResponse(
            items=warehouses,
            total=total['count'],
            page=page,
            page_size=page_size,
            total_pages=(total['count'] + page_size - 1) // page_size
        )

    @staticmethod
    async def update_warehouse(warehouse_id: str, warehouse: WarehouseUpdate) -> Optional[WarehouseResponse]:
        """Update warehouse"""
        # Build dynamic update query
        update_fields = []
        values = []
        param_count = 1

        for field, value in warehouse.dict(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field} = ${param_count}")
                values.append(value)
                param_count += 1

        if not update_fields:
            return await WarehouseService.get_warehouse(warehouse_id)

        query = f"""
        UPDATE warehouses 
        SET {', '.join(update_fields)}, updated_at = NOW()
        WHERE id = ${param_count}
        RETURNING *
        """
        values.append(warehouse_id)

        result = await db.fetchrow(query, *values)
        if result:
            return WarehouseResponse(**dict(result))
        return None

    @staticmethod
    async def delete_warehouse(warehouse_id: str) -> bool:
        """Soft delete warehouse"""
        query = """
        UPDATE warehouses 
        SET is_active = false, updated_at = NOW()
        WHERE id = $1
        """
        result = await db.execute(query, warehouse_id)
        return "UPDATE 1" in result
