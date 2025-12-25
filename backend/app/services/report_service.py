"""Report service for generating admin reports."""
from datetime import datetime, timedelta
from sqlalchemy import func
from ..models.tower import Tower
from ..models.flat import Flat
from ..models.booking import Booking, BookingStatus
from ..models.lease import Lease, LeaseStatus
from .. import db


class ReportService:
    """Service class for generating reports."""
    
    @staticmethod
    def get_occupancy_report():
        """
        Get occupancy statistics per tower.
        
        Returns:
            List of dicts with occupancy data per tower
        """
        towers = Tower.query.all()
        report = []
        
        for tower in towers:
            total_flats = Flat.query.filter(Flat.tower_id == tower.id).count()
            occupied_flats = Flat.query.filter(
                Flat.tower_id == tower.id,
                Flat.is_available == False
            ).count()
            vacant_flats = total_flats - occupied_flats
            occupancy_percentage = (occupied_flats / total_flats * 100) if total_flats > 0 else 0
            
            report.append({
                'tower_id': tower.id,
                'tower_name': tower.name,
                'total_flats': total_flats,
                'occupied_flats': occupied_flats,
                'vacant_flats': vacant_flats,
                'occupancy_percentage': round(occupancy_percentage, 2)
            })
        
        return report
    
    @staticmethod
    def get_booking_report(period='month'):
        """
        Get booking counts by status and time period.
        
        Args:
            period: Time period for the report ('week', 'month', 'year')
        
        Returns:
            Dict with booking statistics
        """
        now = datetime.utcnow()
        
        # Determine date range based on period
        if period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'year':
            start_date = now - timedelta(days=365)
        else:  # default to month
            start_date = now - timedelta(days=30)
        
        # Get total counts by status
        total_pending = Booking.query.filter(
            Booking.status == BookingStatus.PENDING
        ).count()
        
        total_approved = Booking.query.filter(
            Booking.status == BookingStatus.APPROVED
        ).count()
        
        total_declined = Booking.query.filter(
            Booking.status == BookingStatus.DECLINED
        ).count()
        
        # Get counts for the specified period
        period_pending = Booking.query.filter(
            Booking.status == BookingStatus.PENDING,
            Booking.created_at >= start_date
        ).count()
        
        period_approved = Booking.query.filter(
            Booking.status == BookingStatus.APPROVED,
            Booking.created_at >= start_date
        ).count()
        
        period_declined = Booking.query.filter(
            Booking.status == BookingStatus.DECLINED,
            Booking.created_at >= start_date
        ).count()
        
        return {
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': now.isoformat(),
            'total': {
                'pending': total_pending,
                'approved': total_approved,
                'declined': total_declined,
                'total': total_pending + total_approved + total_declined
            },
            'period_counts': {
                'pending': period_pending,
                'approved': period_approved,
                'declined': period_declined,
                'total': period_pending + period_approved + period_declined
            }
        }
    
    @staticmethod
    def get_payment_report():
        """
        Get mock payment data showing expected vs received rent per month.
        
        Returns:
            Dict with payment statistics (mock data)
        """
        # Get all active leases
        active_leases = Lease.query.filter(
            Lease.status == LeaseStatus.ACTIVE
        ).all()
        
        # Calculate expected monthly rent
        expected_monthly = sum(float(lease.monthly_rent) for lease in active_leases)
        
        # Generate mock payment data for the last 6 months
        now = datetime.utcnow()
        monthly_data = []
        
        for i in range(6):
            month_date = now - timedelta(days=30 * i)
            month_name = month_date.strftime('%B %Y')
            
            # Mock data: assume 95% collection rate with some variation
            import random
            random.seed(month_date.month + month_date.year)  # Consistent mock data
            collection_rate = random.uniform(0.90, 0.98)
            
            received = expected_monthly * collection_rate
            
            monthly_data.append({
                'month': month_name,
                'expected': round(expected_monthly, 2),
                'received': round(received, 2),
                'collection_rate': round(collection_rate * 100, 2)
            })
        
        return {
            'active_leases_count': len(active_leases),
            'total_expected_monthly': round(expected_monthly, 2),
            'monthly_breakdown': monthly_data,
            'note': 'Payment data is mock/simulated for demonstration purposes'
        }
