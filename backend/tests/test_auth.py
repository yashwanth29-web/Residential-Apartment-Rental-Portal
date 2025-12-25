"""Tests for authentication endpoints."""
import json


def test_register_success(client):
    """Test successful user registration."""
    response = client.post('/api/auth/register', 
        data=json.dumps({
            'email': 'test@example.com',
            'password': 'password123',
            'name': 'Test User',
            'phone': '1234567890'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'token' in data
    assert 'user' in data
    assert data['user']['email'] == 'test@example.com'
    assert data['user']['name'] == 'Test User'
    assert data['user']['role'] == 'user'


def test_register_duplicate_email(client):
    """Test registration with duplicate email."""
    # First registration
    client.post('/api/auth/register',
        data=json.dumps({
            'email': 'test@example.com',
            'password': 'password123',
            'name': 'Test User'
        }),
        content_type='application/json'
    )
    
    # Second registration with same email
    response = client.post('/api/auth/register',
        data=json.dumps({
            'email': 'test@example.com',
            'password': 'password456',
            'name': 'Another User'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error']['code'] == 'AUTH_EMAIL_EXISTS'


def test_register_missing_fields(client):
    """Test registration with missing required fields."""
    response = client.post('/api/auth/register',
        data=json.dumps({
            'email': 'test@example.com'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error']['code'] == 'VALIDATION_ERROR'


def test_login_success(client):
    """Test successful login."""
    # Register first
    client.post('/api/auth/register',
        data=json.dumps({
            'email': 'test@example.com',
            'password': 'password123',
            'name': 'Test User'
        }),
        content_type='application/json'
    )
    
    # Login
    response = client.post('/api/auth/login',
        data=json.dumps({
            'email': 'test@example.com',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'token' in data
    assert 'user' in data


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post('/api/auth/login',
        data=json.dumps({
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['error']['code'] == 'AUTH_INVALID_CREDENTIALS'


def test_get_current_user(client):
    """Test getting current user info."""
    # Register and get token
    register_response = client.post('/api/auth/register',
        data=json.dumps({
            'email': 'test@example.com',
            'password': 'password123',
            'name': 'Test User'
        }),
        content_type='application/json'
    )
    token = json.loads(register_response.data)['token']
    
    # Get current user
    response = client.get('/api/auth/me',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['email'] == 'test@example.com'


def test_get_current_user_unauthorized(client):
    """Test getting current user without token."""
    response = client.get('/api/auth/me')
    
    assert response.status_code == 401


def test_admin_required_decorator(client, app):
    """Test that admin_required decorator blocks non-admin users."""
    from app.decorators import admin_required
    from flask import Blueprint
    
    # Create a test blueprint with admin-protected route
    test_bp = Blueprint('test_admin', __name__)
    
    @test_bp.route('/test-admin')
    @admin_required()
    def admin_only():
        return {'message': 'admin access granted'}
    
    app.register_blueprint(test_bp)
    
    # Register a regular user
    register_response = client.post('/api/auth/register',
        data=json.dumps({
            'email': 'user@example.com',
            'password': 'password123',
            'name': 'Regular User'
        }),
        content_type='application/json'
    )
    user_token = json.loads(register_response.data)['token']
    
    # Try to access admin route with regular user token
    response = client.get('/test-admin',
        headers={'Authorization': f'Bearer {user_token}'}
    )
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert data['error']['code'] == 'AUTH_FORBIDDEN'


def test_jwt_contains_role(client):
    """Test that JWT token contains user role in claims."""
    from flask_jwt_extended import decode_token
    
    # Register a user
    register_response = client.post('/api/auth/register',
        data=json.dumps({
            'email': 'test@example.com',
            'password': 'password123',
            'name': 'Test User'
        }),
        content_type='application/json'
    )
    token = json.loads(register_response.data)['token']
    
    # Decode the token and check claims
    with client.application.app_context():
        decoded = decode_token(token)
        assert 'role' in decoded
        assert decoded['role'] == 'user'
