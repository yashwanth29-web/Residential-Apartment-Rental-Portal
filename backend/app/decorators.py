"""Custom decorators for route protection."""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt

from .models import UserRole


def admin_required():
    """
    Decorator that requires the user to be an admin.
    Must be used after @jwt_required() or includes JWT verification.
    
    Usage:
        @app.route('/admin/resource')
        @admin_required()
        def admin_resource():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Verify JWT is present and valid
            verify_jwt_in_request()
            
            # Get the claims from the token
            claims = get_jwt()
            role = claims.get('role')
            
            # Check if user has admin role
            if role != UserRole.ADMIN.value:
                return jsonify({
                    'error': {
                        'code': 'AUTH_FORBIDDEN',
                        'message': 'Admin access required'
                    }
                }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def get_current_user_id():
    """
    Helper function to get the current user's ID from JWT identity.
    
    Returns:
        int: The user ID from the JWT token
    """
    return get_jwt_identity()


def get_current_user_role():
    """
    Helper function to get the current user's role from JWT claims.
    
    Returns:
        str: The user role from the JWT token
    """
    claims = get_jwt()
    return claims.get('role')
