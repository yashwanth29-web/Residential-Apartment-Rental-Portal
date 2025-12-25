"""Amenity service for handling amenity-related business logic."""
from ..models.amenity import Amenity, AmenityType
from .. import db


class AmenityService:
    """Service class for amenity operations."""
    
    @staticmethod
    def get_amenities(amenity_type=None):
        """
        Get all amenities with optional type filter.
        
        Args:
            amenity_type: Filter by amenity type (gym, pool, parking, common)
        
        Returns:
            List of Amenity objects
        """
        query = Amenity.query
        
        if amenity_type is not None:
            query = query.filter(Amenity.type == amenity_type)
        
        return query.all()
    
    @staticmethod
    def get_amenity_by_id(amenity_id):
        """
        Get an amenity by its ID.
        
        Args:
            amenity_id: The ID of the amenity
        
        Returns:
            Amenity object or None if not found
        """
        return db.session.get(Amenity, amenity_id)
    
    @staticmethod
    def create_amenity(name, amenity_type, description=None, hours=None, fee=None):
        """
        Create a new amenity.
        
        Args:
            name: The name of the amenity
            amenity_type: The type of amenity (gym, pool, parking, common)
            description: Optional description
            hours: Optional availability hours
            fee: Optional fee
        
        Returns:
            Tuple of (Amenity, error_message)
        """
        # Validate amenity type
        try:
            if isinstance(amenity_type, str):
                amenity_type = AmenityType(amenity_type)
        except ValueError:
            valid_types = [t.value for t in AmenityType]
            return None, f'Invalid amenity type. Must be one of: {", ".join(valid_types)}'
        
        amenity = Amenity(
            name=name,
            type=amenity_type,
            description=description,
            hours=hours,
            fee=fee
        )
        
        db.session.add(amenity)
        db.session.commit()
        
        return amenity, None
    
    @staticmethod
    def update_amenity(amenity_id, name=None, amenity_type=None, description=None, hours=None, fee=None):
        """
        Update an existing amenity.
        
        Args:
            amenity_id: The ID of the amenity to update
            name: Optional new name
            amenity_type: Optional new type
            description: Optional new description
            hours: Optional new hours
            fee: Optional new fee
        
        Returns:
            Tuple of (Amenity, error_message)
        """
        amenity = db.session.get(Amenity, amenity_id)
        
        if amenity is None:
            return None, 'Amenity not found'
        
        if name is not None:
            amenity.name = name
        
        if amenity_type is not None:
            try:
                if isinstance(amenity_type, str):
                    amenity_type = AmenityType(amenity_type)
                amenity.type = amenity_type
            except ValueError:
                valid_types = [t.value for t in AmenityType]
                return None, f'Invalid amenity type. Must be one of: {", ".join(valid_types)}'
        
        if description is not None:
            amenity.description = description
        
        if hours is not None:
            amenity.hours = hours
        
        if fee is not None:
            amenity.fee = fee
        
        db.session.commit()
        
        return amenity, None
    
    @staticmethod
    def delete_amenity(amenity_id):
        """
        Delete an amenity.
        
        Args:
            amenity_id: The ID of the amenity to delete
        
        Returns:
            Tuple of (success, error_message)
        """
        amenity = db.session.get(Amenity, amenity_id)
        
        if amenity is None:
            return False, 'Amenity not found'
        
        db.session.delete(amenity)
        db.session.commit()
        
        return True, None
