"""Tests for booking endpoints."""
import json
from app.models import Tower, Flat, Booking, BookingStatus
from app import db


def create_test_tower_and_flat(app, is_available=True):
    """Helper to create a tower and flat for testing."""
    with app.app_context():
        tower = Tower(name='Test Tower', address='123 Test St', total_floors=10)
        db.session.add(tower)
        db.session.commit()
        
        flat = Flat(
            tower_id=tower.id,
            unit_number='101',
            floor=1,
            bedrooms=2,
            bathrooms=1,
            area_sqft=1000,
            rent=1500.00,
            is_available=is_available
        )
        db.session.add(flat)
        db.session.commit()
        
        return tower.id, flat.id


def register_and_get_token(client, email='test@example.com'):
    """Helper to register a user and get their token."""
    response = client.post('/api/auth/register',
        data=json.dumps({
            'email': email,
            'password': 'password123',
            'name': 'Test User'
        }),
        content_type='application/json'
    )
    return json.loads(response.data)['token']


def test_create_booking_success(client, app):
    """Test successful booking creation."""
    tower_id, flat_id = create_test_tower_and_flat(app)
    token = register_and_get_token(client)
    
    response = client.post('/api/bookings',
        data=json.dumps({
            'flat_id': flat_id,
            'requested_date': '2025-02-01'
        }),
        content_type='application/json',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['flat_id'] == flat_id
    assert data['status'] == 'pending'
    assert data['requested_date'] == '2025-02-01'


def test_create_booking_unavailable_flat(client, app):
    """Test booking creation for unavailable flat."""
    tower_id, flat_id = create_test_tower_and_flat(app, is_available=False)
    token = register_and_get_token(client)
    
    response = client.post('/api/bookings',
        data=json.dumps({
            'flat_id': flat_id,
            'requested_date': '2025-02-01'
        }),
        content_type='application/json',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error']['code'] == 'BOOKING_UNAVAILABLE'


def test_create_booking_duplicate_pending(client, app):
    """Test duplicate pending booking prevention."""
    tower_id, flat_id = create_test_tower_and_flat(app)
    token = register_and_get_token(client)
    
    # First booking
    client.post('/api/bookings',
        data=json.dumps({
            'flat_id': flat_id,
            'requested_date': '2025-02-01'
        }),
        content_type='application/json',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    # Second booking for same flat
    response = client.post('/api/bookings',
        data=json.dumps({
            'flat_id': flat_id,
            'requested_date': '2025-03-01'
        }),
        content_type='application/json',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 409
    data = json.loads(response.data)
    assert data['error']['code'] == 'BOOKING_DUPLICATE'


def test_create_booking_nonexistent_flat(client, app):
    """Test booking creation for non-existent flat."""
    token = register_and_get_token(client)
    
    response = client.post('/api/bookings',
        data=json.dumps({
            'flat_id': 9999,
            'requested_date': '2025-02-01'
        }),
        content_type='application/json',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['error']['code'] == 'RESOURCE_NOT_FOUND'


def test_create_booking_missing_fields(client, app):
    """Test booking creation with missing fields."""
    token = register_and_get_token(client)
    
    response = client.post('/api/bookings',
        data=json.dumps({
            'flat_id': 1
        }),
        content_type='application/json',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error']['code'] == 'VALIDATION_ERROR'


def test_create_booking_unauthorized(client, app):
    """Test booking creation without authentication."""
    tower_id, flat_id = create_test_tower_and_flat(app)
    
    response = client.post('/api/bookings',
        data=json.dumps({
            'flat_id': flat_id,
            'requested_date': '2025-02-01'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 401


def test_get_user_bookings(client, app):
    """Test getting user's bookings."""
    tower_id, flat_id = create_test_tower_and_flat(app)
    token = register_and_get_token(client)
    
    # Create a booking
    client.post('/api/bookings',
        data=json.dumps({
            'flat_id': flat_id,
            'requested_date': '2025-02-01'
        }),
        content_type='application/json',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    # Get bookings
    response = client.get('/api/bookings',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['flat_id'] == flat_id


def test_get_user_bookings_isolation(client, app):
    """Test that users only see their own bookings."""
    tower_id, flat_id = create_test_tower_and_flat(app)
    
    # Create booking as user1
    token1 = register_and_get_token(client, 'user1@example.com')
    client.post('/api/bookings',
        data=json.dumps({
            'flat_id': flat_id,
            'requested_date': '2025-02-01'
        }),
        content_type='application/json',
        headers={'Authorization': f'Bearer {token1}'}
    )
    
    # Get bookings as user2
    token2 = register_and_get_token(client, 'user2@example.com')
    response = client.get('/api/bookings',
        headers={'Authorization': f'Bearer {token2}'}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 0


def test_get_booking_by_id(client, app):
    """Test getting a specific booking by ID."""
    tower_id, flat_id = create_test_tower_and_flat(app)
    token = register_and_get_token(client)
    
    # Create a booking
    create_response = client.post('/api/bookings',
        data=json.dumps({
            'flat_id': flat_id,
            'requested_date': '2025-02-01'
        }),
        content_type='application/json',
        headers={'Authorization': f'Bearer {token}'}
    )
    booking_id = json.loads(create_response.data)['id']
    
    # Get booking by ID
    response = client.get(f'/api/bookings/{booking_id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == booking_id
    assert data['flat_id'] == flat_id


def test_get_booking_not_found(client, app):
    """Test getting a non-existent booking."""
    token = register_and_get_token(client)
    
    response = client.get('/api/bookings/9999',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['error']['code'] == 'RESOURCE_NOT_FOUND'


def test_get_booking_other_user(client, app):
    """Test that users cannot access other users' bookings."""
    tower_id, flat_id = create_test_tower_and_flat(app)
    
    # Create booking as user1
    token1 = register_and_get_token(client, 'user1@example.com')
    create_response = client.post('/api/bookings',
        data=json.dumps({
            'flat_id': flat_id,
            'requested_date': '2025-02-01'
        }),
        content_type='application/json',
        headers={'Authorization': f'Bearer {token1}'}
    )
    booking_id = json.loads(create_response.data)['id']
    
    # Try to get booking as user2
    token2 = register_and_get_token(client, 'user2@example.com')
    response = client.get(f'/api/bookings/{booking_id}',
        headers={'Authorization': f'Bearer {token2}'}
    )
    
    assert response.status_code == 404
