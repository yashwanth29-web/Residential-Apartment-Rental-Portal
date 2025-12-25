def register_blueprints(app):
    """Register all blueprints with the Flask app."""
    from .auth import auth_bp
    from .flats import flats_bp
    from .amenities import amenities_bp
    from .bookings import bookings_bp
    from .admin import admin_bp
    from .towers import towers_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(flats_bp)
    app.register_blueprint(amenities_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(towers_bp)
