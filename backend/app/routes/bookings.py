"""Booking routes for managing rental requests."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..services.booking_service import BookingService

bookings_bp = Blueprint('bookings', __name__, url_prefix='/api/bookings')


@bookings_bp.route('', methods=['POST'])
@jwt_required()
def create_booking():
    """
    Create a new booking request.
    
    Request body:
        - flat_id: integer (required)
        - requested_date: string in YYYY-MM-DD format (required)
    
    Returns:
        201: Booking created successfully
        400: Validation error or flat unavailable
        404: Flat not found
        409: Duplicate pending booking
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Request body is required'
            }
        }), 400
    
    flat_id = data.get('flat_id')
    requested_date = data.get('requested_date')
    
    # Validate required fields
    if flat_id is None or requested_date is None:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'flat_id and requested_date are required',
                'details': {
                    'flat_id': 'Required' if flat_id is None else None,
                    'requested_date': 'Required' if requested_date is None else None
                }
            }
        }), 400
    
    booking, error = BookingService.create_booking(user_id, flat_id, requested_date)
    
    if error:
        # Determine appropriate error code and status
        if 'not found' in error.lower():
            return jsonify({
                'error': {
                    'code': 'RESOURCE_NOT_FOUND',
                    'message': error
                }
            }), 404
        elif 'not available' in error.lower():
            return jsonify({
                'error': {
                    'code': 'BOOKING_UNAVAILABLE',
                    'message': error
                }
            }), 400
        elif 'already have' in error.lower():
            return jsonify({
                'error': {
                    'code': 'BOOKING_DUPLICATE',
                    'message': error
                }
            }), 409
        else:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': error
                }
            }), 400
    
    return jsonify(booking.to_dict()), 201


@bookings_bp.route('', methods=['GET'])
@jwt_required()
def get_user_bookings():
    """
    Get all bookings for the authenticated user.
    
    Returns:
        200: List of user's bookings
    """
    user_id = get_jwt_identity()
    
    bookings = BookingService.get_user_bookings(user_id)
    
    return jsonify([booking.to_dict() for booking in bookings]), 200


@bookings_bp.route('/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    """
    Get details of a specific booking.
    
    Path parameters:
        - booking_id: The ID of the booking
    
    Returns:
        200: Booking details
        404: Booking not found or doesn't belong to user
    """
    user_id = get_jwt_identity()
    
    booking = BookingService.get_booking_by_id(booking_id, user_id=user_id)
    
    if booking is None:
        return jsonify({
            'error': {
                'code': 'RESOURCE_NOT_FOUND',
                'message': 'Booking not found'
            }
        }), 404
    
    return jsonify(booking.to_dict()), 200
