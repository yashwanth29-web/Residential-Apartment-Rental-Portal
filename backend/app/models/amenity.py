from enum import Enum
from .. import db


class AmenityType(str, Enum):
    GYM = 'gym'
    POOL = 'pool'
    PARKING = 'parking'
    COMMON = 'common'


class Amenity(db.Model):
    """Amenity model representing shared facilities."""
    __tablename__ = 'amenities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Enum(AmenityType), nullable=False)
    description = db.Column(db.Text)
    hours = db.Column(db.String(100))
    fee = db.Column(db.Numeric(10, 2))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type.value,
            'description': self.description,
            'hours': self.hours,
            'fee': float(self.fee) if self.fee else None
        }
