"""Tenant service for handling tenant-related business logic."""
from ..models.user import User
from ..models.booking import Booking, BookingStatus
from ..models.lease import Lease, LeaseStatus
from ..models.flat import Flat
from .. import db


class TenantService:
    """Service class for tenant operations."""
    
    @staticmethod
    def get_tenants():
        """
        Get all users with active leases.
        
        Returns:
            List of User objects with active leases
        """
        # Query users who have at least one active lease
        tenants = db.session.query(User).join(
            Booking, User.id == Booking.user_id
        ).join(
            Lease, Booking.id == Lease.booking_id
        ).filter(
            Lease.status == LeaseStatus.ACTIVE
        ).distinct().all()
        
        return tenants
    
    @staticmethod
    def get_tenant_by_id(user_id):
        """
        Get tenant details including active leases.
        
        Args:
            user_id: The ID of the user
        
        Returns:
            Tuple of (User, list of active leases) or (None, None) if not found
        """
        user = db.session.get(User, user_id)
        
        if user is None:
            return None, None
        
        # Get active leases for this user
        active_leases = db.session.query(Lease).join(
            Booking, Lease.booking_id == Booking.id
        ).filter(
            Booking.user_id == user_id,
            Lease.status == LeaseStatus.ACTIVE
        ).all()
        
        return user, active_leases
    
    @staticmethod
    def get_tenant_details(user_id):
        """
        Get comprehensive tenant details including user info, current lease, and payment history.
        
        Args:
            user_id: The ID of the user
        
        Returns:
            Dict with tenant details or None if not found
        """
        user = db.session.get(User, user_id)
        
        if user is None:
            return None
        
        # Get all leases for this user (both active and terminated)
        leases = db.session.query(Lease).join(
            Booking, Lease.booking_id == Booking.id
        ).filter(
            Booking.user_id == user_id
        ).order_by(Lease.start_date.desc()).all()
        
        # Build lease details with flat info
        lease_details = []
        for lease in leases:
            booking = db.session.get(Booking, lease.booking_id)
            flat = db.session.get(Flat, booking.flat_id) if booking else None
            
            lease_info = lease.to_dict()
            if flat:
                lease_info['flat'] = flat.to_dict()
            lease_details.append(lease_info)
        
        return {
            'user': user.to_dict(),
            'leases': lease_details,
            'active_leases_count': sum(1 for l in leases if l.status == LeaseStatus.ACTIVE)
        }
    
    @staticmethod
    def terminate_lease(lease_id):
        """
        Terminate an active lease and mark the flat as available.
        
        Args:
            lease_id: The ID of the lease to terminate
        
        Returns:
            Tuple of (Lease, error_message)
        """
        lease = db.session.get(Lease, lease_id)
        
        if lease is None:
            return None, 'Lease not found'
        
        if lease.status != LeaseStatus.ACTIVE:
            return None, f'Cannot terminate lease with status: {lease.status.value}'
        
        # Update lease status
        lease.status = LeaseStatus.TERMINATED
        
        # Mark flat as available
        booking = db.session.get(Booking, lease.booking_id)
        if booking and booking.flat:
            booking.flat.is_available = True
        
        db.session.commit()
        
        return lease, None
    
    @staticmethod
    def get_lease_by_id(lease_id):
        """
        Get a lease by its ID.
        
        Args:
            lease_id: The ID of the lease
        
        Returns:
            Lease object or None if not found
        """
        return db.session.get(Lease, lease_id)
