"""
Database seed script for demo data.
Creates sample towers, flats, amenities, and demo users.

Demo Credentials:
- Admin: admin@example.com / admin123
- User: user@example.com / user123
"""
import bcrypt
from app import create_app, db
from app.models import User, UserRole, Tower, Flat, Amenity, AmenityType


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def seed_users():
    """Create demo admin and user accounts."""
    users = [
        {
            'email': 'admin@example.com',
            'password': 'admin123',
            'name': 'Admin User',
            'phone': '555-0100',
            'role': UserRole.ADMIN
        },
        {
            'email': 'user@example.com',
            'password': 'user123',
            'name': 'Demo User',
            'phone': '555-0101',
            'role': UserRole.USER
        },
        {
            'email': 'john.doe@example.com',
            'password': 'password123',
            'name': 'John Doe',
            'phone': '555-0102',
            'role': UserRole.USER
        },
        {
            'email': 'jane.smith@example.com',
            'password': 'password123',
            'name': 'Jane Smith',
            'phone': '555-0103',
            'role': UserRole.USER
        }
    ]
    
    created_users = []
    for user_data in users:
        existing = User.query.filter_by(email=user_data['email']).first()
        if not existing:
            user = User(
                email=user_data['email'],
                password_hash=hash_password(user_data['password']),
                name=user_data['name'],
                phone=user_data['phone'],
                role=user_data['role']
            )
            db.session.add(user)
            created_users.append(user_data['email'])
    
    db.session.commit()
    return created_users


def seed_towers():
    """Create sample towers."""
    towers = [
        {
            'name': 'Sunrise Tower',
            'address': '100 Main Street, Downtown',
            'total_floors': 15
        },
        {
            'name': 'Sunset Tower',
            'address': '200 Main Street, Downtown',
            'total_floors': 12
        },
        {
            'name': 'Ocean View Tower',
            'address': '300 Beach Boulevard, Waterfront',
            'total_floors': 20
        }
    ]
    
    created_towers = []
    for tower_data in towers:
        existing = Tower.query.filter_by(name=tower_data['name']).first()
        if not existing:
            tower = Tower(**tower_data)
            db.session.add(tower)
            created_towers.append(tower_data['name'])
    
    db.session.commit()
    return created_towers


def seed_flats():
    """Create sample flats for each tower."""
    towers = Tower.query.all()
    created_flats = []
    
    flat_templates = [
        {'bedrooms': 1, 'bathrooms': 1, 'area_sqft': 650, 'rent': 1200},
        {'bedrooms': 1, 'bathrooms': 1, 'area_sqft': 700, 'rent': 1350},
        {'bedrooms': 2, 'bathrooms': 1, 'area_sqft': 900, 'rent': 1800},
        {'bedrooms': 2, 'bathrooms': 2, 'area_sqft': 1000, 'rent': 2100},
        {'bedrooms': 3, 'bathrooms': 2, 'area_sqft': 1300, 'rent': 2800},
        {'bedrooms': 3, 'bathrooms': 2, 'area_sqft': 1400, 'rent': 3200},
    ]
    
    for tower in towers:
        for floor in range(1, min(tower.total_floors + 1, 6)):  # First 5 floors
            for unit_idx, template in enumerate(flat_templates[:3]):  # 3 units per floor
                unit_number = f'{floor}{str(unit_idx + 1).zfill(2)}'
                
                existing = Flat.query.filter_by(
                    tower_id=tower.id, 
                    unit_number=unit_number
                ).first()
                
                if not existing:
                    # Vary availability - some flats are occupied
                    is_available = not (floor == 1 and unit_idx == 0)
                    
                    flat = Flat(
                        tower_id=tower.id,
                        unit_number=unit_number,
                        floor=floor,
                        bedrooms=template['bedrooms'],
                        bathrooms=template['bathrooms'],
                        area_sqft=template['area_sqft'],
                        rent=template['rent'] + (floor * 50),  # Higher floors cost more
                        is_available=is_available
                    )
                    db.session.add(flat)
                    created_flats.append(f"{tower.name} - {unit_number}")
    
    db.session.commit()
    return created_flats


def seed_amenities():
    """Create sample amenities."""
    amenities = [
        {
            'name': 'Fitness Center',
            'type': AmenityType.GYM,
            'description': 'State-of-the-art gym with cardio and weight equipment',
            'hours': '5:00 AM - 11:00 PM',
            'fee': None
        },
        {
            'name': 'Rooftop Pool',
            'type': AmenityType.POOL,
            'description': 'Heated rooftop swimming pool with city views',
            'hours': '6:00 AM - 10:00 PM',
            'fee': None
        },
        {
            'name': 'Underground Parking',
            'type': AmenityType.PARKING,
            'description': 'Secure underground parking garage with assigned spots',
            'hours': '24/7',
            'fee': 150.00
        },
        {
            'name': 'Guest Parking',
            'type': AmenityType.PARKING,
            'description': 'Visitor parking available on first-come basis',
            'hours': '24/7',
            'fee': 10.00
        },
        {
            'name': 'Community Lounge',
            'type': AmenityType.COMMON,
            'description': 'Spacious lounge area with TV, games, and kitchen',
            'hours': '8:00 AM - 10:00 PM',
            'fee': None
        },
        {
            'name': 'Business Center',
            'type': AmenityType.COMMON,
            'description': 'Co-working space with printers and meeting rooms',
            'hours': '7:00 AM - 9:00 PM',
            'fee': None
        },
        {
            'name': 'Yoga Studio',
            'type': AmenityType.GYM,
            'description': 'Dedicated yoga and meditation room',
            'hours': '6:00 AM - 9:00 PM',
            'fee': None
        },
        {
            'name': 'BBQ Area',
            'type': AmenityType.COMMON,
            'description': 'Outdoor grilling stations with seating areas',
            'hours': '10:00 AM - 9:00 PM',
            'fee': 25.00
        }
    ]
    
    created_amenities = []
    for amenity_data in amenities:
        existing = Amenity.query.filter_by(name=amenity_data['name']).first()
        if not existing:
            amenity = Amenity(**amenity_data)
            db.session.add(amenity)
            created_amenities.append(amenity_data['name'])
    
    db.session.commit()
    return created_amenities


def seed_database():
    """Run all seed functions."""
    print("Starting database seeding...")
    
    print("\n1. Creating demo users...")
    users = seed_users()
    print(f"   Created {len(users)} users: {users}")
    
    print("\n2. Creating towers...")
    towers = seed_towers()
    print(f"   Created {len(towers)} towers: {towers}")
    
    print("\n3. Creating flats...")
    flats = seed_flats()
    print(f"   Created {len(flats)} flats")
    
    print("\n4. Creating amenities...")
    amenities = seed_amenities()
    print(f"   Created {len(amenities)} amenities: {amenities}")
    
    print("\n" + "=" * 50)
    print("Database seeding complete!")
    print("=" * 50)
    print("\nDemo Credentials:")
    print("  Admin: admin@example.com / admin123")
    print("  User:  user@example.com / user123")
    print("=" * 50)


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_database()
