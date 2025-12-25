from datetime import datetime
from enum import Enum
from .. import db


class BookingStatus(str, Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    DECLINED = 'declined'


class Booking(db.Model):
    """Booking model representing a rental request."""
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    flat_id = db.Column(db.Integer, db.ForeignKey('flats.id'), nullable=False)
    status = db.Column(db.Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    requested_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    lease = db.relationship('Lease', backref='booking', uselist=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'flat_id': self.flat_id,
            'flat': self.flat.to_dict() if self.flat else None,
            'status': self.status.value,
            'requested_date': self.requested_date.isoformat() if self.requested_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
