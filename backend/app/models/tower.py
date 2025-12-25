from .. import db


# Association table for tower-amenity many-to-many relationship
tower_amenities = db.Table('tower_amenities',
    db.Column('tower_id', db.Integer, db.ForeignKey('towers.id'), primary_key=True),
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenities.id'), primary_key=True)
)


class Tower(db.Model):
    """Tower model representing a building in the complex."""
    __tablename__ = 'towers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text)
    total_floors = db.Column(db.Integer, nullable=False)
    flats_per_floor = db.Column(db.Integer, nullable=False, default=4)
    
    # Relationships
    flats = db.relationship('Flat', backref='tower', lazy=True)
    amenities = db.relationship('Amenity', secondary=tower_amenities, lazy='subquery',
                                backref=db.backref('towers', lazy=True))
    
    def to_dict(self, include_amenities=False):
        result = {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'total_floors': self.total_floors,
            'flats_per_floor': self.flats_per_floor
        }
        if include_amenities:
            result['amenities'] = [amenity.to_dict() for amenity in self.amenities]
            result['amenity_ids'] = [amenity.id for amenity in self.amenities]
        return result
