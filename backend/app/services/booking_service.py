"""Booking service for handling booking-related business logic."""
from datetime import datetime, date
from ..models.booking import Booking, BookingStatus
from ..models.flat import Flat
from ..models.lease import Lease, LeaseStatus
from .. import db


class BookingService:
    """Service class for booking operations."""
    
    @staticmethod
    def create_booking(user_id, flat_id, requested_date):
        """
        Create a new booking request.
        
        Args:
            user_id: The ID of the user making the booking
            flat_id: The ID of the flat to book
            requested_date: The requested move-in date
        
        Returns:
            Tuple of (Booking, error_message)
        """
        # Convert user_id to int if it's a string
        user_id = int(user_id)
        
        # Check if flat exists
        flat = db.session.get(Flat, flat_id)
        if flat is None:
            return None, 'Flat not found'
        
        # Check if flat is available
        if not flat.is_available:
            return None, 'Flat is not available for booking'
        
        # Check for duplicate pending booking
        existing_booking = Booking.query.filter(
            Booking.user_id == user_id,
            Booking.flat_id == flat_id,
            Booking.status == BookingStatus.PENDING
        ).first()
        
        if existing_booking:
            return None, 'You already have a pending booking for this flat'
        
        # Parse requested_date if it's a string
        if isinstance(requested_date, str):
            try:
                requested_date = datetime.strptime(requested_date, '%Y-%m-%d').date()
            except ValueError:
                return None, 'Invalid date format. Use YYYY-MM-DD'
        
        # Create the booking
        booking = Booking(
            user_id=user_id,
            flat_id=flat_id,
            requested_date=requested_date,
            status=BookingStatus.PENDING
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return booking, None
    
    @staticmethod
    def get_user_bookings(user_id):
        """
        Get all bookings for a specific user.
        
        Args:
            user_id: The ID of the user
        
        Returns:
            List of Booking objects
        """
        # Convert user_id to int if it's a string
        user_id = int(user_id)
        return Booking.query.filter(Booking.user_id == user_id).order_by(Booking.created_at.desc()).all()
    
    @staticmethod
    def get_booking_by_id(booking_id, user_id=None):
        """
        Get a booking by its ID.
        
        Args:
            booking_id: The ID of the booking
            user_id: If provided, only return if booking belongs to this user
        
        Returns:
            Booking object or None if not found
        """
        booking = db.session.get(Booking, booking_id)
        
        if booking is None:
            return None
        
        # If user_id is provided, verify ownership (convert to int for comparison)
        if user_id is not None and booking.user_id != int(user_id):
            return None
        
        return booking

    
    @staticmethod
    def get_all_bookings():
        """
        Get all bookings (admin only).
        
        Returns:
            List of all Booking objects
        """
        return Booking.query.order_by(Booking.created_at.desc()).all()
    
    @staticmethod
    def approve_booking(booking_id):
        """
        Approve a pending booking and create a lease.
        
        Args:
            booking_id: The ID of the booking to approve
        
        Returns:
            Tuple of (Booking, error_message)
        """
        booking = db.session.get(Booking, booking_id)
        
        if booking is None:
            return None, 'Booking not found'
        
        if booking.status != BookingStatus.PENDING:
            return None, f'Cannot approve booking with status: {booking.status.value}'
        
        # Update booking status
        booking.status = BookingStatus.APPROVED
        
        # Create lease record
        lease = Lease(
            booking_id=booking.id,
            start_date=booking.requested_date,
            monthly_rent=booking.flat.rent,
            status=LeaseStatus.ACTIVE
        )
        db.session.add(lease)
        
        # Mark flat as unavailable
        booking.flat.is_available = False
        
        db.session.commit()
        
        return booking, None
    
    @staticmethod
    def decline_booking(booking_id):
        """
        Decline a pending booking.
        
        Args:
            booking_id: The ID of the booking to decline
        
        Returns:
            Tuple of (Booking, error_message)
        """
        booking = db.session.get(Booking, booking_id)
        
        if booking is None:
            return None, 'Booking not found'
        
        if booking.status != BookingStatus.PENDING:
            return None, f'Cannot decline booking with status: {booking.status.value}'
        
        # Update booking status
        booking.status = BookingStatus.DECLINED
        
        db.session.commit()
        
        return booking, None
