"""Flat service for handling flat-related business logic."""
from sqlalchemy.exc import IntegrityError
from ..models.flat import Flat
from ..models.tower import Tower
from .. import db


class FlatService:
    """Service class for flat operations."""
    
    @staticmethod
    def get_flats(tower_id=None, bedrooms=None, min_rent=None, max_rent=None, include_unavailable=False):
        """
        Get flats with optional filters.
        
        Args:
            tower_id: Filter by tower ID
            bedrooms: Filter by number of bedrooms
            min_rent: Filter by minimum rent
            max_rent: Filter by maximum rent
            include_unavailable: If True, include unavailable flats (admin only)
        
        Returns:
            List of Flat objects matching the filters
        """
        query = Flat.query
        
        # Only show available flats for non-admin users
        if not include_unavailable:
            query = query.filter(Flat.is_available == True)
        
        # Apply filters
        if tower_id is not None:
            query = query.filter(Flat.tower_id == tower_id)
        
        if bedrooms is not None:
            query = query.filter(Flat.bedrooms == bedrooms)
        
        if min_rent is not None:
            query = query.filter(Flat.rent >= min_rent)
        
        if max_rent is not None:
            query = query.filter(Flat.rent <= max_rent)
        
        return query.all()
    
    @staticmethod
    def get_flat_by_id(flat_id, include_unavailable=False):
        """
        Get a flat by its ID.
        
        Args:
            flat_id: The ID of the flat
            include_unavailable: If True, return even if unavailable (admin only)
        
        Returns:
            Flat object or None if not found
        """
        flat = Flat.query.get(flat_id)
        
        if flat is None:
            return None
        
        # For non-admin users, only return available flats
        if not include_unavailable and not flat.is_available:
            return None
        
        return flat
    
    @staticmethod
    def get_all_flats():
        """
        Get all flats (admin only).
        
        Returns:
            List of all Flat objects
        """
        return Flat.query.all()
    
    @staticmethod
    def create_flat(tower_id, unit_number, floor, bedrooms, bathrooms, rent, area_sqft=None, is_available=True):
        """
        Create a new flat.
        
        Args:
            tower_id: ID of the tower
            unit_number: Unit number within the tower
            floor: Floor number
            bedrooms: Number of bedrooms
            bathrooms: Number of bathrooms
            rent: Monthly rent
            area_sqft: Area in square feet (optional)
            is_available: Availability status (default True)
        
        Returns:
            Tuple of (Flat object, error message or None)
        """
        # Check if tower exists
        tower = Tower.query.get(tower_id)
        if tower is None:
            return None, "Tower not found"
        
        try:
            flat = Flat(
                tower_id=tower_id,
                unit_number=unit_number,
                floor=floor,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                rent=rent,
                area_sqft=area_sqft,
                is_available=is_available
            )
            db.session.add(flat)
            db.session.commit()
            return flat, None
        except IntegrityError:
            db.session.rollback()
            return None, f"Unit number '{unit_number}' already exists in this tower"
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def update_flat(flat_id, tower_id=None, unit_number=None, floor=None, bedrooms=None, 
                    bathrooms=None, rent=None, area_sqft=None, is_available=None):
        """
        Update an existing flat.
        
        Args:
            flat_id: The ID of the flat to update
            tower_id: New tower ID (optional)
            unit_number: New unit number (optional)
            floor: New floor number (optional)
            bedrooms: New number of bedrooms (optional)
            bathrooms: New number of bathrooms (optional)
            rent: New monthly rent (optional)
            area_sqft: New area in square feet (optional)
            is_available: New availability status (optional)
        
        Returns:
            Tuple of (Flat object, error message or None)
        """
        flat = Flat.query.get(flat_id)
        
        if flat is None:
            return None, "Flat not found"
        
        # If changing tower, verify it exists
        if tower_id is not None and tower_id != flat.tower_id:
            tower = Tower.query.get(tower_id)
            if tower is None:
                return None, "Tower not found"
        
        try:
            if tower_id is not None:
                flat.tower_id = tower_id
            if unit_number is not None:
                flat.unit_number = unit_number
            if floor is not None:
                flat.floor = floor
            if bedrooms is not None:
                flat.bedrooms = bedrooms
            if bathrooms is not None:
                flat.bathrooms = bathrooms
            if rent is not None:
                flat.rent = rent
            if area_sqft is not None:
                flat.area_sqft = area_sqft
            if is_available is not None:
                flat.is_available = is_available
            
            db.session.commit()
            return flat, None
        except IntegrityError:
            db.session.rollback()
            return None, f"Unit number '{unit_number}' already exists in this tower"
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def delete_flat(flat_id):
        """
        Delete a flat.
        
        Args:
            flat_id: The ID of the flat to delete
        
        Returns:
            Tuple of (success boolean, error message or None)
        """
        flat = Flat.query.get(flat_id)
        
        if flat is None:
            return False, "Flat not found"
        
        try:
            db.session.delete(flat)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)
