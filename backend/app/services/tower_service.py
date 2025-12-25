"""Tower service for handling tower-related business logic."""
from ..models.tower import Tower
from ..models.flat import Flat
from ..models.amenity import Amenity
from .. import db


class TowerService:
    """Service class for tower operations."""
    
    @staticmethod
    def get_all_towers(include_amenities=False):
        """
        Get all towers.
        
        Args:
            include_amenities: If True, include amenity details
        
        Returns:
            List of Tower objects
        """
        return Tower.query.all()
    
    @staticmethod
    def get_tower_by_id(tower_id):
        """
        Get a tower by its ID.
        
        Args:
            tower_id: The ID of the tower
        
        Returns:
            Tower object or None if not found
        """
        return Tower.query.get(tower_id)
    
    @staticmethod
    def create_tower(name, address, total_floors, flats_per_floor=4, amenity_ids=None):
        """
        Create a new tower.
        
        Args:
            name: Tower name
            address: Tower address
            total_floors: Total number of floors
            flats_per_floor: Number of flats per floor (default 4)
            amenity_ids: List of amenity IDs to assign to the tower
        
        Returns:
            Tuple of (Tower object, error message or None)
        """
        try:
            tower = Tower(
                name=name,
                address=address,
                total_floors=total_floors,
                flats_per_floor=flats_per_floor
            )
            
            # Assign amenities if provided
            if amenity_ids:
                amenities = Amenity.query.filter(Amenity.id.in_(amenity_ids)).all()
                tower.amenities = amenities
            
            db.session.add(tower)
            db.session.commit()
            return tower, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def update_tower(tower_id, name=None, address=None, total_floors=None, flats_per_floor=None, amenity_ids=None):
        """
        Update an existing tower.
        
        Args:
            tower_id: The ID of the tower to update
            name: New tower name (optional)
            address: New tower address (optional)
            total_floors: New total floors (optional)
            flats_per_floor: New flats per floor (optional)
            amenity_ids: List of amenity IDs to assign (optional, replaces existing)
        
        Returns:
            Tuple of (Tower object, error message or None)
        """
        tower = Tower.query.get(tower_id)
        
        if tower is None:
            return None, "Tower not found"
        
        try:
            if name is not None:
                tower.name = name
            if address is not None:
                tower.address = address
            if total_floors is not None:
                tower.total_floors = total_floors
            if flats_per_floor is not None:
                tower.flats_per_floor = flats_per_floor
            if amenity_ids is not None:
                amenities = Amenity.query.filter(Amenity.id.in_(amenity_ids)).all()
                tower.amenities = amenities
            
            db.session.commit()
            return tower, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def delete_tower(tower_id):
        """
        Delete a tower if it has no associated flats.
        
        Args:
            tower_id: The ID of the tower to delete
        
        Returns:
            Tuple of (success boolean, error message or None)
        """
        tower = Tower.query.get(tower_id)
        
        if tower is None:
            return False, "Tower not found"
        
        # Check if tower has associated flats
        flat_count = Flat.query.filter(Flat.tower_id == tower_id).count()
        if flat_count > 0:
            return False, f"Cannot delete tower with {flat_count} associated flat(s)"
        
        try:
            db.session.delete(tower)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)
