"""Public tower routes for listing towers."""
from flask import Blueprint, jsonify

from ..services.tower_service import TowerService

towers_bp = Blueprint('towers', __name__, url_prefix='/api/towers')


@towers_bp.route('', methods=['GET'])
def get_towers():
    """
    Get list of all towers (public endpoint for filtering).
    
    Returns:
        200: List of towers
    """
    towers = TowerService.get_all_towers()
    return jsonify([tower.to_dict() for tower in towers]), 200


@towers_bp.route('/<int:tower_id>', methods=['GET'])
def get_tower(tower_id):
    """
    Get a specific tower with its amenities (public endpoint).
    
    Path parameters:
        - tower_id: The ID of the tower
    
    Returns:
        200: Tower details with amenities
        404: Tower not found
    """
    tower = TowerService.get_tower_by_id(tower_id)
    
    if tower is None:
        return jsonify({
            'error': {
                'code': 'RESOURCE_NOT_FOUND',
                'message': 'Tower not found'
            }
        }), 404
    
    return jsonify(tower.to_dict(include_amenities=True)), 200
