from flask import Blueprint

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    from .auth import auth_bp
    from .users import users_bp
    from .fitness import fitness_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(fitness_bp)