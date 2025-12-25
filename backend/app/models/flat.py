from datetime import datetime
from .. import db


class Flat(db.Model):
    """Flat model representing an apartment unit."""
    __tablename__ = 'flats'
    
    id = db.Column(db.Integer, primary_key=True)
    tower_id = db.Column(db.Integer, db.ForeignKey('towers.id'), nullable=False)
    unit_number = db.Column(db.String(20), nullable=False)
    floor = db.Column(db.Integer, nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    area_sqft = db.Column(db.Integer)
    rent = db.Column(db.Numeric(10, 2), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint: unit number must be unique within a tower
    __table_args__ = (
        db.UniqueConstraint('tower_id', 'unit_number', name='unique_unit_per_tower'),
    )
    
    # Relationships
    bookings = db.relationship('Booking', backref='flat', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tower_id': self.tower_id,
            'tower_name': self.tower.name if self.tower else None,
            'unit_number': self.unit_number,
            'floor': self.floor,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'area_sqft': self.area_sqft,
            'rent': float(self.rent) if self.rent else None,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
