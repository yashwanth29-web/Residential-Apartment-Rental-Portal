"""Admin routes for managing towers, flats, amenities, bookings, and tenants."""
from flask import Blueprint, request, jsonify

from ..decorators import admin_required
from ..services.tower_service import TowerService
from ..services.flat_service import FlatService

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# ============================================================================
# Tower Management Routes
# ============================================================================

@admin_bp.route('/towers', methods=['GET'])
@admin_required()
def get_towers():
    """
    Get all towers with their amenities.
    
    Returns:
        200: List of all towers with amenities
    """
    towers = TowerService.get_all_towers()
    return jsonify([tower.to_dict(include_amenities=True) for tower in towers]), 200


@admin_bp.route('/towers', methods=['POST'])
@admin_required()
def create_tower():
    """
    Create a new tower.
    
    Request body:
        - name: string (required)
        - address: string (optional)
        - total_floors: integer (required)
        - flats_per_floor: integer (optional, default 4)
        - amenity_ids: array of integers (optional)
    
    Returns:
        201: Tower created successfully
        400: Validation error
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Request body is required'
            }
        }), 400
    
    name = data.get('name')
    address = data.get('address')
    total_floors = data.get('total_floors')
    flats_per_floor = data.get('flats_per_floor', 4)
    amenity_ids = data.get('amenity_ids', [])
    
    # Validate required fields
    if not name:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Tower name is required',
                'details': {'name': 'Required'}
            }
        }), 400
    
    if total_floors is None:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Total floors is required',
                'details': {'total_floors': 'Required'}
            }
        }), 400
    
    if not isinstance(total_floors, int) or total_floors < 1:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Total floors must be a positive integer',
                'details': {'total_floors': 'Must be a positive integer'}
            }
        }), 400
    
    if not isinstance(flats_per_floor, int) or flats_per_floor < 1:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Flats per floor must be a positive integer',
                'details': {'flats_per_floor': 'Must be a positive integer'}
            }
        }), 400
    
    tower, error = TowerService.create_tower(name, address, total_floors, flats_per_floor, amenity_ids)
    
    if error:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': error
            }
        }), 400
    
    return jsonify(tower.to_dict(include_amenities=True)), 201


@admin_bp.route('/towers/<int:tower_id>', methods=['GET'])
@admin_required()
def get_tower(tower_id):
    """
    Get a specific tower by ID with amenities.
    
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


@admin_bp.route('/towers/<int:tower_id>', methods=['PUT'])
@admin_required()
def update_tower(tower_id):
    """
    Update an existing tower.
    
    Path parameters:
        - tower_id: The ID of the tower
    
    Request body:
        - name: string (optional)
        - address: string (optional)
        - total_floors: integer (optional)
        - flats_per_floor: integer (optional)
        - amenity_ids: array of integers (optional)
    
    Returns:
        200: Tower updated successfully
        400: Validation error
        404: Tower not found
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Request body is required'
            }
        }), 400
    
    name = data.get('name')
    address = data.get('address')
    total_floors = data.get('total_floors')
    flats_per_floor = data.get('flats_per_floor')
    amenity_ids = data.get('amenity_ids')
    
    # Validate total_floors if provided
    if total_floors is not None:
        if not isinstance(total_floors, int) or total_floors < 1:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Total floors must be a positive integer',
                    'details': {'total_floors': 'Must be a positive integer'}
                }
            }), 400
    
    # Validate flats_per_floor if provided
    if flats_per_floor is not None:
        if not isinstance(flats_per_floor, int) or flats_per_floor < 1:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Flats per floor must be a positive integer',
                    'details': {'flats_per_floor': 'Must be a positive integer'}
                }
            }), 400
    
    tower, error = TowerService.update_tower(tower_id, name, address, total_floors, flats_per_floor, amenity_ids)
    
    if error:
        if "not found" in error.lower():
            return jsonify({
                'error': {
                    'code': 'RESOURCE_NOT_FOUND',
                    'message': error
                }
            }), 404
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': error
            }
        }), 400
    
    return jsonify(tower.to_dict(include_amenities=True)), 200


@admin_bp.route('/towers/<int:tower_id>', methods=['DELETE'])
@admin_required()
def delete_tower(tower_id):
    """
    Delete a tower.
    
    Path parameters:
        - tower_id: The ID of the tower
    
    Returns:
        200: Tower deleted successfully
        400: Cannot delete tower with associated flats
        404: Tower not found
    """
    success, error = TowerService.delete_tower(tower_id)
    
    if not success:
        if "not found" in error.lower():
            return jsonify({
                'error': {
                    'code': 'RESOURCE_NOT_FOUND',
                    'message': error
                }
            }), 404
        if "cannot delete" in error.lower():
            return jsonify({
                'error': {
                    'code': 'CONSTRAINT_VIOLATION',
                    'message': error
                }
            }), 400
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': error
            }
        }), 400
    
    return jsonify({'message': 'Tower deleted successfully'}), 200



# ============================================================================
# Flat Management Routes
# ============================================================================

@admin_bp.route('/flats', methods=['GET'])
@admin_required()
def get_all_flats():
    """
    Get all flats (including unavailable).
    
    Returns:
        200: List of all flats
    """
    flats = FlatService.get_all_flats()
    return jsonify([flat.to_dict() for flat in flats]), 200


@admin_bp.route('/flats', methods=['POST'])
@admin_required()
def create_flat():
    """
    Create a new flat.
    
    Request body:
        - tower_id: integer (required)
        - unit_number: string (required)
        - floor: integer (required)
        - bedrooms: integer (required)
        - bathrooms: integer (required)
        - rent: number (required)
        - area_sqft: integer (optional)
        - is_available: boolean (optional, default true)
    
    Returns:
        201: Flat created successfully
        400: Validation error
        404: Tower not found
        409: Unit number already exists in tower
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Request body is required'
            }
        }), 400
    
    tower_id = data.get('tower_id')
    unit_number = data.get('unit_number')
    floor = data.get('floor')
    bedrooms = data.get('bedrooms')
    bathrooms = data.get('bathrooms')
    rent = data.get('rent')
    area_sqft = data.get('area_sqft')
    is_available = data.get('is_available', True)
    
    # Validate required fields
    errors = {}
    if tower_id is None:
        errors['tower_id'] = 'Required'
    if not unit_number:
        errors['unit_number'] = 'Required'
    if floor is None:
        errors['floor'] = 'Required'
    if bedrooms is None:
        errors['bedrooms'] = 'Required'
    if bathrooms is None:
        errors['bathrooms'] = 'Required'
    if rent is None:
        errors['rent'] = 'Required'
    
    if errors:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Missing required fields',
                'details': errors
            }
        }), 400
    
    # Validate field types
    if not isinstance(tower_id, int):
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Tower ID must be an integer',
                'details': {'tower_id': 'Must be an integer'}
            }
        }), 400
    
    if not isinstance(floor, int) or floor < 0:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Floor must be a non-negative integer',
                'details': {'floor': 'Must be a non-negative integer'}
            }
        }), 400
    
    if not isinstance(bedrooms, int) or bedrooms < 0:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Bedrooms must be a non-negative integer',
                'details': {'bedrooms': 'Must be a non-negative integer'}
            }
        }), 400
    
    if not isinstance(bathrooms, int) or bathrooms < 0:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Bathrooms must be a non-negative integer',
                'details': {'bathrooms': 'Must be a non-negative integer'}
            }
        }), 400
    
    if not isinstance(rent, (int, float)) or rent < 0:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Rent must be a non-negative number',
                'details': {'rent': 'Must be a non-negative number'}
            }
        }), 400
    
    flat, error = FlatService.create_flat(
        tower_id=tower_id,
        unit_number=unit_number,
        floor=floor,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        rent=rent,
        area_sqft=area_sqft,
        is_available=is_available
    )
    
    if error:
        if "tower not found" in error.lower():
            return jsonify({
                'error': {
                    'code': 'RESOURCE_NOT_FOUND',
                    'message': error
                }
            }), 404
        if "already exists" in error.lower():
            return jsonify({
                'error': {
                    'code': 'RESOURCE_CONFLICT',
                    'message': error
                }
            }), 409
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': error
            }
        }), 400
    
    return jsonify(flat.to_dict()), 201


@admin_bp.route('/flats/<int:flat_id>', methods=['GET'])
@admin_required()
def get_flat(flat_id):
    """
    Get a specific flat by ID.
    
    Path parameters:
        - flat_id: The ID of the flat
    
    Returns:
        200: Flat details
        404: Flat not found
    """
    flat = FlatService.get_flat_by_id(flat_id, include_unavailable=True)
    
    if flat is None:
        return jsonify({
            'error': {
                'code': 'RESOURCE_NOT_FOUND',
                'message': 'Flat not found'
            }
        }), 404
    
    return jsonify(flat.to_dict()), 200


@admin_bp.route('/flats/<int:flat_id>', methods=['PUT'])
@admin_required()
def update_flat(flat_id):
    """
    Update an existing flat.
    
    Path parameters:
        - flat_id: The ID of the flat
    
    Request body:
        - tower_id: integer (optional)
        - unit_number: string (optional)
        - floor: integer (optional)
        - bedrooms: integer (optional)
        - bathrooms: integer (optional)
        - rent: number (optional)
        - area_sqft: integer (optional)
        - is_available: boolean (optional)
    
    Returns:
        200: Flat updated successfully
        400: Validation error
        404: Flat or Tower not found
        409: Unit number already exists in tower
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Request body is required'
            }
        }), 400
    
    tower_id = data.get('tower_id')
    unit_number = data.get('unit_number')
    floor = data.get('floor')
    bedrooms = data.get('bedrooms')
    bathrooms = data.get('bathrooms')
    rent = data.get('rent')
    area_sqft = data.get('area_sqft')
    is_available = data.get('is_available')
    
    # Validate field types if provided
    if tower_id is not None and not isinstance(tower_id, int):
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Tower ID must be an integer',
                'details': {'tower_id': 'Must be an integer'}
            }
        }), 400
    
    if floor is not None and (not isinstance(floor, int) or floor < 0):
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Floor must be a non-negative integer',
                'details': {'floor': 'Must be a non-negative integer'}
            }
        }), 400
    
    if bedrooms is not None and (not isinstance(bedrooms, int) or bedrooms < 0):
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Bedrooms must be a non-negative integer',
                'details': {'bedrooms': 'Must be a non-negative integer'}
            }
        }), 400
    
    if bathrooms is not None and (not isinstance(bathrooms, int) or bathrooms < 0):
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Bathrooms must be a non-negative integer',
                'details': {'bathrooms': 'Must be a non-negative integer'}
            }
        }), 400
    
    if rent is not None and (not isinstance(rent, (int, float)) or rent < 0):
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Rent must be a non-negative number',
                'details': {'rent': 'Must be a non-negative number'}
            }
        }), 400
    
    flat, error = FlatService.update_flat(
        flat_id=flat_id,
        tower_id=tower_id,
        unit_number=unit_number,
        floor=floor,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        rent=rent,
        area_sqft=area_sqft,
        is_available=is_available
    )
    
    if error:
        if "not found" in error.lower():
            return jsonify({
                'error': {
                    'code': 'RESOURCE_NOT_FOUND',
                    'message': error
                }
            }), 404
        if "already exists" in error.lower():
            return jsonify({
                'error': {
                    'code': 'RESOURCE_CONFLICT',
                    'message': error
                }
            }), 409
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': error
            }
        }), 400
    
    return jsonify(flat.to_dict()), 200


@admin_bp.route('/flats/<int:flat_id>', methods=['DELETE'])
@admin_required()
def delete_flat(flat_id):
    """
    Delete a flat.
    
    Path parameters:
        - flat_id: The ID of the flat
    
    Returns:
        200: Flat deleted successfully
        404: Flat not found
    """
    success, error = FlatService.delete_flat(flat_id)
    
    if not success:
        if "not found" in error.lower():
            return jsonify({
                'error': {
                    'code': 'RESOURCE_NOT_FOUND',
                    'message': error
                }
            }), 404
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': error
            }
        }), 400
    
    return jsonify({'message': 'Flat deleted successfully'}), 200



# ============================================================================
# Amenity Management Routes
# ============================================================================

from ..services.amenity_service import AmenityService


@admin_bp.route('/amenities', methods=['GET'])
@admin_required()
def get_amenities():
    """
    Get all amenities.
    
    Returns:
        200: List of all amenities
    """
    amenities = AmenityService.get_amenities()
    return jsonify([amenity.to_dict() for amenity in amenities]), 200


@admin_bp.route('/amenities', methods=['POST'])
@admin_required()
def create_amenity():
    """
    Create a new amenity.
    
    Request body:
        - name: string (required)
        - type: string (required) - one of: gym, pool, parking, common
        - description: string (optional)
        - hours: string (optional)
        - fee: number (optional)
    
    Returns:
        201: Amenity created successfully
        400: Validation error
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Request body is required'
            }
        }), 400
    
    name = data.get('name')
    amenity_type = data.get('type')
    description = data.get('description')
    hours = data.get('hours')
    fee = data.get('fee')
    
    # Validate required fields
    errors = {}
    if not name:
        errors['name'] = 'Required'
    if not amenity_type:
        errors['type'] = 'Required'
    
    if errors:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Missing required fields',
                'details': errors
            }
        }), 400
    
    # Validate fee if provided
    if fee is not None and (not isinstance(fee, (int, float)) or fee < 0):
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Fee must be a non-negative number',
                'details': {'fee': 'Must be a non-negative number'}
            }
        }), 400
    
    amenity, error = AmenityService.create_amenity(
        name=name,
        amenity_type=amenity_type,
        description=description,
        hours=hours,
        fee=fee
    )
    
    if error:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': error
            }
        }), 400
    
    return jsonify(amenity.to_dict()), 201


@admin_bp.route('/amenities/<int:amenity_id>', methods=['GET'])
@admin_required()
def get_amenity(amenity_id):
    """
    Get a specific amenity by ID.
    
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


@admin_bp.route('/amenities/<int:amenity_id>', methods=['PUT'])
@admin_required()
def update_amenity(amenity_id):
    """
    Update an existing amenity.
    
    Path parameters:
        - amenity_id: The ID of the amenity
    
    Request body:
        - name: string (optional)
        - type: string (optional) - one of: gym, pool, parking, common
        - description: string (optional)
        - hours: string (optional)
        - fee: number (optional)
    
    Returns:
        200: Amenity updated successfully
        400: Validation error
        404: Amenity not found
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Request body is required'
            }
        }), 400
    
    name = data.get('name')
    amenity_type = data.get('type')
    description = data.get('description')
    hours = data.get('hours')
    fee = data.get('fee')
    
    # Validate fee if provided
    if fee is not None and (not isinstance(fee, (int, float)) or fee < 0):
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Fee must be a non-negative number',
                'details': {'fee': 'Must be a non-negative number'}
            }
        }), 400
    
    amenity, error = AmenityService.update_amenity(
        amenity_id=amenity_id,
        name=name,
        amenity_type=amenity_type,
        description=description,
        hours=hours,
        fee=fee
    )
    
    if error:
        if "not found" in error.lower():
            return jsonify({
                'error': {
                    'code': 'RESOURCE_NOT_FOUND',
                    'message': error
                }
            }), 404
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': error
            }
        }), 400
    
    return jsonify(amenity.to_dict()), 200


@admin_bp.route('/amenities/<int:amenity_id>', methods=['DELETE'])
@admin_required()
def delete_amenity(amenity_id):
    """
    Delete an amenity.
    
    Path parameters:
        - amenity_id: The ID of the amenity
    
    Returns:
        200: Amenity deleted successfully
        404: Amenity not found
    """
    success, error = AmenityService.delete_amenity(amenity_id)
    
    if not success:
        if "not found" in error.lower():
            return jsonify({
                'error': {
                    'code': 'RESOURCE_NOT_FOUND',
                    'message': error
                }
            }), 404
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': error
            }
        }), 400
    
    return jsonify({'message': 'Amenity deleted successfully'}), 200


# ============================================================================
# Booking Management Routes
# ============================================================================

from ..services.booking_service import BookingService


@admin_bp.route('/bookings', methods=['GET'])
@admin_required()
def get_all_bookings():
    """
    Get all bookings.
    
    Returns:
        200: List of all bookings
    """
    bookings = BookingService.get_all_bookings()
    return jsonify([booking.to_dict() for booking in bookings]), 200


@admin_bp.route('/bookings/<int:booking_id>', methods=['GET'])
@admin_required()
def get_booking(booking_id):
    """
    Get a specific booking by ID.
    
    Path parameters:
        - booking_id: The ID of the booking
    
    Returns:
        200: Booking details
        404: Booking not found
    """
    booking = BookingService.get_booking_by_id(booking_id)
    
    if booking is None:
        return jsonify({
            'error': {
                'code': 'RESOURCE_NOT_FOUND',
                'message': 'Booking not found'
            }
        }), 404
    
    return jsonify(booking.to_dict()), 200


@admin_bp.route('/bookings/<int:booking_id>/approve', methods=['PUT'])
@admin_required()
def approve_booking(booking_id):
    """
    Approve a pending booking.
    
    Path parameters:
        - booking_id: The ID of the booking
    
    Returns:
        200: Booking approved successfully
        400: Cannot approve booking (not pending)
        404: Booking not found
    """
    booking, error = BookingService.approve_booking(booking_id)
    
    if error:
        if "not found" in error.lower():
            return jsonify({
                'error': {
                    'code': 'RESOURCE_NOT_FOUND',
                    'message': error
                }
            }), 404
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': error
            }
        }), 400
    
    # Include lease info in response
    response = booking.to_dict()
    if booking.lease:
        response['lease'] = booking.lease.to_dict()
    
    return jsonify(response), 200


@admin_bp.route('/bookings/<int:booking_id>/decline', methods=['PUT'])
@admin_required()
def decline_booking(booking_id):
    """
    Decline a pending booking.
    
    Path parameters:
        - booking_id: The ID of the booking
    
    Returns:
        200: Booking declined successfully
        400: Cannot decline booking (not pending)
        404: Booking not found
    """
    booking, error = BookingService.decline_booking(booking_id)
    
    if error:
        if "not found" in error.lower():
            return jsonify({
                'error': {
                    'code': 'RESOURCE_NOT_FOUND',
                    'message': error
                }
            }), 404
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': error
            }
        }), 400
    
    return jsonify(booking.to_dict()), 200


# ============================================================================
# Tenant Management Routes
# ============================================================================

from ..services.tenant_service import TenantService


@admin_bp.route('/tenants', methods=['GET'])
@admin_required()
def get_tenants():
    """
    Get all users with active leases.
    
    Returns:
        200: List of tenants with active leases
    """
    tenants = TenantService.get_tenants()
    return jsonify([tenant.to_dict() for tenant in tenants]), 200


@admin_bp.route('/tenants/<int:user_id>', methods=['GET'])
@admin_required()
def get_tenant(user_id):
    """
    Get tenant details including user info, leases, and payment history.
    
    Path parameters:
        - user_id: The ID of the user/tenant
    
    Returns:
        200: Tenant details with leases
        404: Tenant not found
    """
    tenant_details = TenantService.get_tenant_details(user_id)
    
    if tenant_details is None:
        return jsonify({
            'error': {
                'code': 'RESOURCE_NOT_FOUND',
                'message': 'Tenant not found'
            }
        }), 404
    
    return jsonify(tenant_details), 200


@admin_bp.route('/leases/<int:lease_id>', methods=['DELETE'])
@admin_required()
def terminate_lease(lease_id):
    """
    Terminate an active lease.
    
    Path parameters:
        - lease_id: The ID of the lease to terminate
    
    Returns:
        200: Lease terminated successfully
        400: Cannot terminate lease (not active)
        404: Lease not found
    """
    lease, error = TenantService.terminate_lease(lease_id)
    
    if error:
        if "not found" in error.lower():
            return jsonify({
                'error': {
                    'code': 'RESOURCE_NOT_FOUND',
                    'message': error
                }
            }), 404
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': error
            }
        }), 400
    
    return jsonify({
        'message': 'Lease terminated successfully',
        'lease': lease.to_dict()
    }), 200



# ============================================================================
# Report Routes
# ============================================================================

from ..services.report_service import ReportService


@admin_bp.route('/reports/occupancy', methods=['GET'])
@admin_required()
def get_occupancy_report():
    """
    Get occupancy statistics per tower.
    
    Returns:
        200: Occupancy report with stats per tower
    """
    report = ReportService.get_occupancy_report()
    return jsonify(report), 200


@admin_bp.route('/reports/bookings', methods=['GET'])
@admin_required()
def get_booking_report():
    """
    Get booking counts by status and time period.
    
    Query parameters:
        - period: 'week', 'month', or 'year' (default: 'month')
    
    Returns:
        200: Booking report with counts by status
    """
    period = request.args.get('period', 'month')
    
    if period not in ['week', 'month', 'year']:
        period = 'month'
    
    report = ReportService.get_booking_report(period)
    return jsonify(report), 200


@admin_bp.route('/reports/payments', methods=['GET'])
@admin_required()
def get_payment_report():
    """
    Get mock payment data showing expected vs received rent.
    
    Returns:
        200: Payment report with monthly breakdown
    """
    report = ReportService.get_payment_report()
    return jsonify(report), 200
