import asyncio
from app.database import db, supabase
from app.services.warehouse_service import WarehouseService
from app.models.warehouse import WarehouseCreate


async def seed_initial_data():
    """Seed initial data for testing"""

    await db.connect()

    # Create sample warehouses
    warehouses = [
        WarehouseCreate(
            id="WH001",
            name="Main Warehouse Delhi",
            address="123 Industrial Area, Gurgaon",
            city="Delhi",
            state="Delhi",
            pincode="110001",
            phone="9876543210"
        ),
        WarehouseCreate(
            id="WH002",
            name="Mumbai Distribution Center",
            address="456 Warehouse Complex, Andheri",
            city="Mumbai",
            state="Maharashtra",
            pincode="400001",
            phone="9876543211"
        )
    ]

    for warehouse in warehouses:
        await WarehouseService.create_warehouse(warehouse)
        print(f"Created warehouse: {warehouse.name}")

    # Create admin user in Supabase
    try:
        admin_user = {
            "email": "admin@logistics.com",
            "password": "admin123",
            "full_name": "System Administrator",
            "role": "admin",
            "warehouse_id": "WH001"
        }

        # This would need to be done through Supabase dashboard or auth API
        print("Please create admin user manually in Supabase dashboard")
        print(f"Admin user details: {admin_user}")

    except Exception as e:
        print(f"Error creating admin user: {e}")

    await db.disconnect()
    print("Data seeding completed!")


if __name__ == "__main__":
    asyncio.run(seed_initial_data())