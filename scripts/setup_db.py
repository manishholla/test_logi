import asyncio
import asyncpg
from app.config import settings


async def setup_database():
    """Initialize database with all required tables and indexes"""

    connection = await asyncpg.connect(settings.database_url)

    # Read and execute migration files
    migration_files = [
        "app/db/migrations/001_initial_schema.sql",
        "app/db/migrations/002_add_indexes.sql",
        "app/db/migrations/003_add_triggers.sql"
    ]

    for file_path in migration_files:
        print(f"Executing migration: {file_path}")
        with open(file_path, 'r') as f:
            migration_sql = f.read()
            await connection.execute(migration_sql)

    await connection.close()
    print("Database setup completed successfully!")


if __name__ == "__main__":
    asyncio.run(setup_database())