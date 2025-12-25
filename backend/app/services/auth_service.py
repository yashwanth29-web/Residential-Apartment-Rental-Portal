"""Authentication service for user registration and login."""
import bcrypt
from flask_jwt_extended import create_access_token
from ..models import User, UserRole
from .. import db


class AuthService:
    """Service class for authentication operations."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    @staticmethod
    def register_user(email: str, password: str, name: str, phone: str = None) -> tuple[User | None, str | None]:
        """
        Register a new user.
        
        Returns:
            tuple: (User object, None) on success, (None, error_message) on failure
        """
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return None, "Email already registered"
        
        # Validate required fields
        if not email or not password or not name:
            return None, "Email, password, and name are required"
        
        # Create new user
        password_hash = AuthService.hash_password(password)
        user = User(
            email=email,
            password_hash=password_hash,
            name=name,
            phone=phone,
            role=UserRole.USER
        )
        
        db.session.add(user)
        db.session.commit()
        
        return user, None
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> tuple[User | None, str | None]:
        """
        Authenticate a user with email and password.
        
        Returns:
            tuple: (User object, None) on success, (None, error_message) on failure
        """
        if not email or not password:
            return None, "Email and password are required"
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return None, "Invalid credentials"
        
        if not AuthService.verify_password(password, user.password_hash):
            return None, "Invalid credentials"
        
        return user, None
    
    @staticmethod
    def generate_token(user: User) -> str:
        """Generate a JWT token for the user."""
        # Use user ID as string identity and add role as additional claims
        additional_claims = {'role': user.role.value}
        return create_access_token(identity=str(user.id), additional_claims=additional_claims)
    
    @staticmethod
    def get_user_by_id(user_id: int | str) -> User | None:
        """Get a user by their ID."""
        return db.session.get(User, int(user_id))
