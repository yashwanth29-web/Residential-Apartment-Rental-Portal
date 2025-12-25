"""Authentication routes for user registration and login."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Request body:
        - email: string (required)
        - password: string (required)
        - name: string (required)
        - phone: string (optional)
    
    Returns:
        201: User created successfully with token
        400: Validation error or email already exists
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Request body is required'
            }
        }), 400
    
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    phone = data.get('phone')
    
    # Validate required fields
    if not email or not password or not name:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Email, password, and name are required',
                'details': {
                    'email': 'Required' if not email else None,
                    'password': 'Required' if not password else None,
                    'name': 'Required' if not name else None
                }
            }
        }), 400
    
    user, error = AuthService.register_user(email, password, name, phone)
    
    if error:
        return jsonify({
            'error': {
                'code': 'AUTH_EMAIL_EXISTS' if 'already' in error else 'VALIDATION_ERROR',
                'message': error
            }
        }), 400
    
    token = AuthService.generate_token(user)
    
    return jsonify({
        'token': token,
        'user': user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login a user.
    
    Request body:
        - email: string (required)
        - password: string (required)
    
    Returns:
        200: Login successful with token
        401: Invalid credentials
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Request body is required'
            }
        }), 400
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Email and password are required'
            }
        }), 400
    
    user, error = AuthService.authenticate_user(email, password)
    
    if error:
        return jsonify({
            'error': {
                'code': 'AUTH_INVALID_CREDENTIALS',
                'message': error
            }
        }), 401
    
    token = AuthService.generate_token(user)
    
    return jsonify({
        'token': token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get the current authenticated user's information.
    
    Returns:
        200: User information
        401: Not authenticated
    """
    user_id = get_jwt_identity()
    
    user = AuthService.get_user_by_id(user_id)
    
    if not user:
        return jsonify({
            'error': {
                'code': 'RESOURCE_NOT_FOUND',
                'message': 'User not found'
            }
        }), 404
    
    return jsonify(user.to_dict()), 200
