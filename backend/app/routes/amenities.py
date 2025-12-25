"""Amenity routes for viewing shared facilities."""
from flask import Blueprint, request, jsonify

from ..services.amenity_service import AmenityService

amenities_bp = Blueprint('amenities', __name__, url_prefix='/api/amenities')


@amenities_bp.route('', methods=['GET'])
def get_amenities():
    """
    Get list of all amenities.
    
    Query parameters:
        - type: Filter by amenity type (gym, pool, parking, common)
    
    Returns:
        200: List of amenities
    """
    amenity_type = request.args.get('type')
    
    amenities = AmenityService.get_amenities(amenity_type=amenity_type)
    
    return jsonify([amenity.to_dict() for amenity in amenities]), 200


@amenities_bp.route('/<int:amenity_id>', methods=['GET'])
def get_amenity(amenity_id):
    """
    Get details of a specific amenity.
    
    Path parameters:
        - amenity_id: The ID of the amenity
    
    Returns:
        200: Amenity details
        404: Amenity not found
    """
    amenity = AmenityService.get_amenity_by_id(amenity_id)
    
    if amenity is None:
        return jsonify({
            'error': {
                'code': 'RESOURCE_NOT_FOUND',
                'message': 'Amenity not found'
            }
        }), 404
    
    return jsonify(amenity.to_dict()), 200
