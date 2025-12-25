from enum import Enum
from .. import db


class LeaseStatus(str, Enum):
    ACTIVE = 'active'
    TERMINATED = 'terminated'


class Lease(db.Model):
    """Lease model representing an active rental agreement."""
    __tablename__ = 'leases'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    monthly_rent = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum(LeaseStatus), default=LeaseStatus.ACTIVE, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'monthly_rent': float(self.monthly_rent) if self.monthly_rent else None,
            'status': self.status.value
        }
