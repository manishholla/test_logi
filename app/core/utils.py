from datetime import datetime, timedelta
from app.database import db


async def archive_old_consignments():
    """Archive consignments older than 6 months"""
    cutoff_date = datetime.now() - timedelta(days=180)

    # Move old consignments to archive table
    query = """
    INSERT INTO consignments_archive 
    SELECT * FROM consignments 
    WHERE created_at < $1 AND status IN ('delivered', 'returned', 'lost')
    """

    await db.execute(query, cutoff_date)

    # Delete from main table
    delete_query = """
    DELETE FROM consignments 
    WHERE created_at < $1 AND status IN ('delivered', 'returned', 'lost')
    """

    await db.execute(delete_query, cutoff_date)
    print(f"Archived consignments older than {cutoff_date}")