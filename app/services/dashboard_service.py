from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app.database import db


class DashboardService:
    @staticmethod
    async def get_dashboard_stats(warehouse_id: Optional[str] = None) -> Dict:
        """Get dashboard statistics"""

        # Base condition for warehouse filtering
        warehouse_condition = f"AND current_warehouse_id = '{warehouse_id}'" if warehouse_id else ""

        # Total consignments
        total_query = f"SELECT COUNT(*) as count FROM consignments WHERE 1=1 {warehouse_condition}"
        total_result = await db.fetchrow(total_query)

        # Pending consignments
        pending_query = f"SELECT COUNT(*) as count FROM consignments WHERE status = 'pending' {warehouse_condition}"
        pending_result = await db.fetchrow(pending_query)

        # In transit consignments
        in_transit_query = f"SELECT COUNT(*) as count FROM consignments WHERE status = 'in_transit' {warehouse_condition}"
        in_transit_result = await db.fetchrow(in_transit_query)

        # Delivered consignments
        delivered_query = f"SELECT COUNT(*) as count FROM consignments WHERE status = 'delivered' {warehouse_condition}"
        delivered_result = await db.fetchrow(delivered_query)

        # Today's consignments
        today_query = f"""
        SELECT COUNT(*) as count FROM consignments 
        WHERE DATE(created_at) = CURRENT_DATE {warehouse_condition}
        """
        today_result = await db.fetchrow(today_query)

        # This week's delivered
        week_delivered_query = f"""
        SELECT COUNT(*) as count FROM consignments 
        WHERE status = 'delivered' 
        AND created_at >= CURRENT_DATE - INTERVAL '7 days' {warehouse_condition}
        """
        week_delivered_result = await db.fetchrow(week_delivered_query)

        return {
            "total_consignments": total_result['count'],
            "pending_consignments": pending_result['count'],
            "in_transit_consignments": in_transit_result['count'],
            "delivered_consignments": delivered_result['count'],
            "today_consignments": today_result['count'],
            "week_delivered": week_delivered_result['count']
        }

    @staticmethod
    async def get_consignments_by_status(warehouse_id: Optional[str] = None, days: int = 30) -> List[Dict]:
        """Get consignments grouped by status"""

        warehouse_condition = f"AND current_warehouse_id = '{warehouse_id}'" if warehouse_id else ""

        query = f"""
        SELECT 
            status,
            COUNT(*) as count
        FROM consignments 
        WHERE created_at >= CURRENT_DATE - INTERVAL '{days} days' {warehouse_condition}
        GROUP BY status
        ORDER BY count DESC
        """

        results = await db.fetch(query)
        return [{"status": row['status'], "count": row['count']} for row in results]

    @staticmethod
    async def get_recent_activities(warehouse_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get recent activities"""

        warehouse_condition = f"AND c.current_warehouse_id = '{warehouse_id}'" if warehouse_id else ""

        query = f"""
        SELECT 
            csl.consignment_id,
            c.tracking_number,
            csl.from_status,
            csl.to_status,
            csl.created_at,
            csl.notes
        FROM consignment_status_log csl
        JOIN consignments c ON csl.consignment_id = c.id
        WHERE 1=1 {warehouse_condition}
        ORDER BY csl.created_at DESC
        LIMIT {limit}
        """

        results = await db.fetch(query)
        return [dict(row) for row in results]

    @staticmethod
    async def get_performance_metrics(warehouse_id: Optional[str] = None, days: int = 30) -> Dict:
        """Get performance metrics"""

        warehouse_condition = f"AND current_warehouse_id = '{warehouse_id}'" if warehouse_id else ""

        # Delivery success rate
        total_query = f"""
        SELECT COUNT(*) as count FROM consignments 
        WHERE created_at >= CURRENT_DATE - INTERVAL '{days} days' 
        AND status IN ('delivered', 'delivery_failed', 'lost') {warehouse_condition}
        """

        delivered_query = f"""
        SELECT COUNT(*) as count FROM consignments 
        WHERE created_at >= CURRENT_DATE - INTERVAL '{days} days' 
        AND status = 'delivered' {warehouse_condition}
        """

        total_result = await db.fetchrow(total_query)
        delivered_result = await db.fetchrow(delivered_query)

        total_final = total_result['count'] or 0
        delivered_final = delivered_result['count'] or 0

        success_rate = (delivered_final / total_final * 100) if total_final > 0 else 0

        # Average delivery time
        avg_delivery_query = f"""
        SELECT AVG(EXTRACT(EPOCH FROM (delivered_at - created_at))/3600) as avg_hours
        FROM consignments 
        WHERE status = 'delivered' 
        AND delivered_at IS NOT NULL
        AND created_at >= CURRENT_DATE - INTERVAL '{days} days' {warehouse_condition}
        """

        avg_delivery_result = await db.fetchrow(avg_delivery_query)
        avg_delivery_hours = avg_delivery_result['avg_hours'] or 0

        return {
            "delivery_success_rate": round(success_rate, 2),
            "average_delivery_time_hours": round(avg_delivery_hours, 2),
            "total_processed": total_final,
            "successfully_delivered": delivered_final
        }

    @staticmethod
    async def get_delivery_trends(warehouse_id: Optional[str] = None, days: int = 30) -> List[Dict]:
        """Get delivery trends over time"""

        warehouse_condition = f"AND current_warehouse_id = '{warehouse_id}'" if warehouse_id else ""

        query = f"""
        SELECT 
            DATE(created_at) as date,
            COUNT(*) as total_consignments,
            COUNT(CASE WHEN status = 'delivered' THEN 1 END) as delivered_consignments
        FROM consignments 
        WHERE created_at >= CURRENT_DATE - INTERVAL '{days} days' {warehouse_condition}
        GROUP BY DATE(created_at)
        ORDER BY date DESC
        """

        results = await db.fetch(query)
        return [dict(row) for row in results]