"""Flat routes for browsing available apartments."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, verify_jwt_in_request

from ..services.flat_service import FlatService
from ..models.user import UserRole

flats_bp = Blueprint('flats', __name__, url_prefix='/api/flats')


def is_admin_user():
    """Check if the current user is an admin (if authenticated)."""
    try:
        verify_jwt_in_request(optional=True)
        claims = get_jwt()
        return claims.get('role') == UserRole.ADMIN.value
    except Exception:
        return False


@flats_bp.route('', methods=['GET'])
def get_flats():
    """
    Get list of flats with optional filters.
    
    Query parameters:
        - tower_id: Filter by tower ID (integer)
        - bedrooms: Filter by number of bedrooms (integer)
        - min_rent: Filter by minimum rent (number)
        - max_rent: Filter by maximum rent (number)
    
    Returns:
        200: List of flats matching filters
        400: Invalid filter parameters
    """
    # Parse query parameters
    tower_id = request.args.get('tower_id', type=int)
    bedrooms = request.args.get('bedrooms', type=int)
    min_rent = request.args.get('min_rent', type=float)
    max_rent = request.args.get('max_rent', type=float)
    
    # Check if user is admin to include unavailable flats
    include_unavailable = is_admin_user()
    
    flats = FlatService.get_flats(
        tower_id=tower_id,
        bedrooms=bedrooms,
        min_rent=min_rent,
        max_rent=max_rent,
        include_unavailable=include_unavailable
    )
    
    return jsonify([flat.to_dict() for flat in flats]), 200


@flats_bp.route('/<int:flat_id>', methods=['GET'])
def get_flat(flat_id):
    """
    Get details of a specific flat.
    
    Path parameters:
        - flat_id: The ID of the flat
    
    Returns:
        200: Flat details
        404: Flat not found
    """
    # For flat details, always show the flat (even if unavailable)
    # This allows users to view details of flats they've booked
    flat = FlatService.get_flat_by_id(flat_id, include_unavailable=True)
    
    if flat is None:
        return jsonify({
            'error': {
                'code': 'RESOURCE_NOT_FOUND',
                'message': 'Flat not found'
            }
        }), 404
    
    return jsonify(flat.to_dict()), 200
